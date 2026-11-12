"""RemoteOK: https://remoteok.com/api (free, no key).

Terms: link back to the job URL and mention "Remote OK" as the source. Don't use their logo.
Response: a JSON list. Item 0 is a legal notice (no "id"); the rest are jobs:
{id, epoch (unix seconds), company, position, description (short teaser, HTML), location, url, ...}
Text often arrives double-encoded ("â€”"), so we repair it with fix_mojibake.
"""

from datetime import UTC, datetime
from typing import Any

from app.ingest.fetchers.base import Fetcher, RawJob
from app.shared.text import fix_mojibake, html_to_text


class RemoteOKFetcher(Fetcher):
    source = "remoteok"
    api_url = "https://remoteok.com/api"

    def parse(self, data: Any) -> list[RawJob]:
        jobs: list[RawJob] = []
        for item in data:
            if "id" not in item:
                continue  # the legal notice, not a job
            if not item.get("position") or not item.get("url"):
                continue

            epoch = item.get("epoch")
            company = item.get("company")
            jobs.append(
                RawJob(
                    source=self.source,
                    source_id=str(item["id"]),
                    url=item["url"],
                    title=fix_mojibake(item["position"]).strip(),
                    company=fix_mojibake(company) if company else None,
                    location=fix_mojibake(item.get("location") or "") or None,
                    description=html_to_text(fix_mojibake(item.get("description") or "")),
                    posted_at=datetime.fromtimestamp(epoch, UTC) if epoch else None,
                )
            )
        return jobs
