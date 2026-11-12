"""The shared shape of a job (RawJob) and the interface every fetcher follows."""

import html
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any

import httpx
from pydantic import BaseModel, field_validator

# A generic, honest User-Agent. No personal details.
USER_AGENT = "JobMatch/0.1 (personal job search tool)"


class RawJob(BaseModel):
    """One job in OUR format, whatever source it came from."""

    source: str
    source_id: str | None
    url: str  # link back to the original posting (required by the sources' terms)
    title: str
    company: str | None
    location: str | None
    description: str  # plain text, no HTML
    posted_at: datetime | None

    @field_validator("title", "company", "location")
    @classmethod
    def decode_html_codes(cls, value: str | None) -> str | None:
        """Sources send "&amp;" instead of "&" in short fields. Fix it for ALL sources here.

        Runs automatically every time a RawJob is created (like a zod .transform()).
        """
        if value is None:
            return None
        return " ".join(html.unescape(value).split())  # also trims extra spaces


class Fetcher(ABC):
    """Base class: each source sets `source` + `api_url` and writes `parse()`.

    fetch() = download + parse. parse() is separate so tests can feed it
    a saved JSON file (fixture) without using the network.
    """

    source: str
    api_url: str

    def fetch(self) -> list[RawJob]:
        return self.parse(self.download())

    def download(self) -> Any:
        response = httpx.get(
            self.api_url,
            headers={"User-Agent": USER_AGENT},
            timeout=30.0,
            follow_redirects=True,
        )
        response.raise_for_status()  # turns 4xx/5xx into an exception
        return response.json()

    @abstractmethod
    def parse(self, data: Any) -> list[RawJob]:
        """Convert this source's JSON into a list of RawJob."""
