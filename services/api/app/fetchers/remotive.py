"""Remotive: https://remotive.com/api/remote-jobs (free, no key).

Terms: max ~4 calls per day, link back to the job URL and mention Remotive as the source.
Jobs are delayed by 24 hours.
Response: {"jobs": [ {id, url, title, company_name, publication_date (ISO, no timezone),
candidate_required_location, description (HTML), salary, ...} ], ...}
"""

from datetime import UTC, datetime
from typing import Any

from app.fetchers.base import Fetcher, RawJob
from app.text import html_to_text


def _parse_date(value: str | None) -> datetime | None:
    if not value:
        return None
    parsed = datetime.fromisoformat(value)
    # Remotive dates have no timezone; we assume UTC
    return parsed if parsed.tzinfo else parsed.replace(tzinfo=UTC)


class RemotiveFetcher(Fetcher):
    source = "remotive"
    api_url = "https://remotive.com/api/remote-jobs"

    def parse(self, data: Any) -> list[RawJob]:
        jobs: list[RawJob] = []
        for item in data.get("jobs", []):
            if not item.get("title") or not item.get("url"):
                continue

            jobs.append(
                RawJob(
                    source=self.source,
                    source_id=str(item["id"]) if item.get("id") else None,
                    url=item["url"],
                    title=item["title"].strip(),
                    company=item.get("company_name"),
                    # e.g. "Worldwide", "USA", "Europe, USA, Canada": important for location_rule
                    location=item.get("candidate_required_location") or None,
                    description=html_to_text(item.get("description") or ""),
                    posted_at=_parse_date(item.get("publication_date")),
                )
            )
        return jobs
