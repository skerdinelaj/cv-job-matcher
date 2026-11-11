"""Arbeitnow: https://www.arbeitnow.com/api/job-board-api (free, no key).

Response: {"data": [ {slug, company_name, title, description (HTML), remote (bool),
url, location, created_at (unix seconds), ...} ], "links": ..., "meta": ...}
"""

from datetime import UTC, datetime
from typing import Any

from app.fetchers.base import Fetcher, RawJob
from app.text import html_to_text


class ArbeitnowFetcher(Fetcher):
    source = "arbeitnow"
    api_url = "https://www.arbeitnow.com/api/job-board-api"

    def parse(self, data: Any) -> list[RawJob]:
        jobs: list[RawJob] = []
        for item in data.get("data", []):
            # Most Arbeitnow jobs are on-site in Germany. Keep only remote ones.
            # (The API's ?remote=true parameter did not filter when we checked.)
            if not item.get("remote"):
                continue
            if not item.get("title") or not item.get("url"):
                continue  # skip broken items instead of crashing the whole run

            created = item.get("created_at")
            jobs.append(
                RawJob(
                    source=self.source,
                    source_id=item.get("slug"),
                    url=item["url"],
                    title=item["title"].strip(),
                    company=item.get("company_name"),
                    location=item.get("location") or None,
                    description=html_to_text(item.get("description") or ""),
                    posted_at=datetime.fromtimestamp(created, UTC) if created else None,
                )
            )
        return jobs
