"""The ONE place where the app talks to an LLM.

Every call goes through `generate_json()`, which:
  - asks Gemini for JSON in the exact shape of a Pydantic class (structured output),
  - waits between calls (rate limit),
  - retries when Google is busy (HTTP 429 or 5xx),
  - logs every call (tokens, time, errors) to the llm_calls table.

In tests, use FakeLLM instead: same method, fixed answers, no API key, no cost.
"""

import logging
import time
from collections.abc import Callable
from typing import Any, Literal, Protocol, TypeVar

import httpx
from google import genai
from google.genai import errors, types
from pydantic import BaseModel

from app.core.config import settings
from app.core.db import SessionLocal
from app.models import LLMCall

logger = logging.getLogger(__name__)

# T = "some Pydantic class". generate_json(schema=JobProfile) returns a JobProfile.
T = TypeVar("T", bound=BaseModel)

# How much hidden "thinking" the model may do before answering.
# More thinking = slower and more output tokens (cost). Simple extraction needs little.
Thinking = Literal["minimal", "low", "medium", "high"]

REQUEST_TIMEOUT_MS = 60_000  # give up on one call after 60s (then retry), never hang for minutes

# Network problems (timeout, connection dropped). google-genai uses httpx or httpx2 inside,
# depending on the version, so we accept both.
try:
    import httpx2

    _NETWORK_ERRORS: tuple[type[Exception], ...] = (httpx.TransportError, httpx2.TransportError)
except ImportError:
    _NETWORK_ERRORS = (httpx.TransportError,)


class LLM(Protocol):
    """The interface the rest of the app depends on (like a TypeScript interface)."""

    model: str

    def generate_json(
        self,
        *,
        step: str,
        prompt: str,
        schema: type[T],
        system: str | None = None,
        thinking: Thinking = "low",
    ) -> T: ...


class DailyQuotaExhaustedError(Exception):
    """The DAILY request limit is used up. Retrying today is pointless: stop the run."""


def _is_daily_quota(exc: Exception) -> bool:
    """429 comes in two kinds: per-minute (wait a bit) and per-day (wait until tomorrow).

    Google names the quota in the error, e.g. "GenerateRequestsPerDayPerProjectPerModel".
    """
    return isinstance(exc, errors.ClientError) and exc.code == 429 and "PerDay" in str(exc)


def _is_retryable(exc: Exception) -> bool:
    """Retry only when trying again can help: Google busy (5xx), per-minute limit (429), network."""
    if isinstance(exc, (errors.ServerError, *_NETWORK_ERRORS)):
        return True
    return isinstance(exc, errors.ClientError) and exc.code == 429 and not _is_daily_quota(exc)


def _short(exc: Exception) -> str:
    """Google's errors are very long. Keep the first line, max 200 characters."""
    return f"{type(exc).__name__}: {str(exc).splitlines()[0] if str(exc) else ''}"[:200]


def _log_call(
    *,
    step: str,
    model: str,
    latency_ms: int,
    ok: bool,
    input_tokens: int | None = None,
    output_tokens: int | None = None,
    error: str | None = None,
) -> None:
    """Save one llm_calls row in its OWN session, so it's kept even if the caller rolls back."""
    try:
        with SessionLocal() as db:
            db.add(
                LLMCall(
                    step=step,
                    model=model,
                    input_tokens=input_tokens,
                    output_tokens=output_tokens,
                    latency_ms=latency_ms,
                    ok=ok,
                    error=error,
                )
            )
            db.commit()
    except Exception:  # logging must never break the real work
        logger.exception("Could not save llm_calls row")


class GeminiLLM:
    """Real LLM calls to Google Gemini."""

    def __init__(self) -> None:
        if not settings.gemini_api_key or not settings.gemini_chat_model:
            raise RuntimeError("Set GEMINI_API_KEY and GEMINI_CHAT_MODEL in .env")
        self.model = settings.gemini_chat_model
        self._client = genai.Client(
            api_key=settings.gemini_api_key,
            http_options=types.HttpOptions(timeout=REQUEST_TIMEOUT_MS),
        )
        self._min_seconds_between_calls = 60.0 / settings.llm_requests_per_minute
        self._last_call_at = 0.0

    def _wait_for_rate_limit(self) -> None:
        """Sleep if the previous call was too recent (simple rate limiter)."""
        elapsed = time.monotonic() - self._last_call_at
        if elapsed < self._min_seconds_between_calls:
            time.sleep(self._min_seconds_between_calls - elapsed)
        self._last_call_at = time.monotonic()

    def generate_json(
        self,
        *,
        step: str,
        prompt: str,
        schema: type[T],
        system: str | None = None,
        thinking: Thinking = "low",
    ) -> T:
        config = types.GenerateContentConfig(
            system_instruction=system,
            temperature=0.0,  # same input -> (nearly) same output; we want facts, not creativity
            response_mime_type="application/json",
            response_schema=schema,  # Gemini must answer in exactly this shape
            thinking_config=types.ThinkingConfig(thinking_level=types.ThinkingLevel(thinking.upper())),
        )

        for attempt in range(1, settings.llm_max_attempts + 1):
            self._wait_for_rate_limit()
            started = time.monotonic()
            try:
                response = self._client.models.generate_content(
                    model=self.model, contents=prompt, config=config
                )
                # Validate the JSON ourselves: if Gemini returns a wrong shape, this raises
                result = schema.model_validate_json(response.text or "")
            except Exception as exc:
                latency_ms = int((time.monotonic() - started) * 1000)
                _log_call(
                    step=step,
                    model=self.model,
                    latency_ms=latency_ms,
                    ok=False,
                    error=f"{type(exc).__name__}: {exc}"[:2000],  # full text in the DB log
                )
                if _is_daily_quota(exc):
                    raise DailyQuotaExhaustedError(
                        f"Daily request limit reached for {self.model}. Try again tomorrow."
                    ) from exc
                if not _is_retryable(exc) or attempt == settings.llm_max_attempts:
                    raise
                wait = 10 * 2 ** (attempt - 1)  # 10s, 20s, 40s (exponential backoff)
                logger.warning("LLM busy (%s). Retry %d in %ds", _short(exc), attempt, wait)
                time.sleep(wait)
                continue

            latency_ms = int((time.monotonic() - started) * 1000)
            usage = response.usage_metadata
            input_tokens = usage.prompt_token_count if usage else None
            # "Thinking" tokens are billed as output, so count them too
            output_tokens = (
                (usage.candidates_token_count or 0) + (usage.thoughts_token_count or 0)
                if usage
                else None
            )
            _log_call(
                step=step,
                model=self.model,
                latency_ms=latency_ms,
                ok=True,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
            )
            return result

        raise RuntimeError("unreachable")  # the loop always returns or raises


class FakeLLM:
    """For tests: no network, no key, no cost.

    Give it a function that gets the prompt and returns a dict;
    the dict is validated into the requested schema, like the real one.
    """

    model = "fake"

    def __init__(self, respond: Callable[[str, str], dict[str, Any]]) -> None:
        self._respond = respond  # (step, prompt) -> dict
        self.calls: list[tuple[str, str]] = []  # tests can check what was asked

    def generate_json(
        self,
        *,
        step: str,
        prompt: str,
        schema: type[T],
        system: str | None = None,
        thinking: Thinking = "low",
    ) -> T:
        self.calls.append((step, prompt))
        return schema.model_validate(self._respond(step, prompt))
