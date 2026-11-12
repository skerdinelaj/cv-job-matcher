"""All settings in one typed object, read from the repo-root .env file.

Usage anywhere in the app:
    from app.config import settings
    settings.database_url
"""

from pathlib import Path
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict

# services/api/app/config.py -> up 3 folders = repo root
ROOT_DIR = Path(__file__).resolve().parents[3]


class Settings(BaseSettings):
    # Pydantic matches each field to an env var with the same name (case-insensitive):
    # database_url <- DATABASE_URL. Real env vars win over the .env file.
    model_config = SettingsConfigDict(
        env_file=ROOT_DIR / ".env",
        extra="ignore",  # .env also has POSTGRES_* for Docker; we don't need them here
    )

    database_url: str

    # Gemini: the ONE place where model names are configured
    gemini_api_key: str = ""
    gemini_chat_model: str = ""
    gemini_embed_model: str = ""

    # LLM safety limits (used by app/llm.py)
    llm_requests_per_minute: int = 10  # stay under the free-tier limit
    llm_max_attempts: int = 4  # 1 try + up to 3 retries when Google is busy

    # Safety: real email sending only when explicitly set to "live"
    email_mode: Literal["dry_run", "live"] = "dry_run"


# One shared instance, created when this module is first imported
settings = Settings()  # type: ignore[call-arg]  # values come from env, not arguments
