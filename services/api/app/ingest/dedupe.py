"""How we recognise "the same job": a fingerprint (content_hash) of company + title."""

import hashlib

from app.ingest.fetchers.base import RawJob
from app.shared.text import normalise_for_hash


def content_hash(job: RawJob) -> str:
    """Fingerprint of a job: company + title, normalised.

    Same company + same title = same job, even if it comes again tomorrow
    or from another source. (Trade-off: the same title for two countries
    counts as one job.)
    """
    key = f"{normalise_for_hash(job.company or '')}|{normalise_for_hash(job.title)}"
    return hashlib.sha256(key.encode("utf-8")).hexdigest()  # 64 hex characters
