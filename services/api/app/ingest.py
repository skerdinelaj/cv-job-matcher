"""Step A of the pipeline: fetch jobs from every source and save the new ones.

Run from services/api:  python -m app.ingest
"""

import hashlib
from datetime import UTC, datetime

from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from app.db import SessionLocal
from app.fetchers import ALL_FETCHERS, Fetcher, RawJob
from app.models import IngestRun, Job
from app.text import normalise_for_hash


def content_hash(job: RawJob) -> str:
    """Fingerprint of a job: company + title, normalised.

    Same company + same title = same job, even if it comes again tomorrow
    or from another source. (Trade-off: the same title for two countries
    counts as one job.)
    """
    key = f"{normalise_for_hash(job.company or '')}|{normalise_for_hash(job.title)}"
    return hashlib.sha256(key.encode("utf-8")).hexdigest()  # 64 hex characters


def save_jobs(db: Session, jobs: list[RawJob]) -> int:
    """Insert jobs; the database skips any whose content_hash already exists.

    Returns how many were really inserted.
    """
    if not jobs:
        return 0

    rows = [{**job.model_dump(), "content_hash": content_hash(job)} for job in jobs]

    # INSERT ... ON CONFLICT (content_hash) DO NOTHING RETURNING id
    # The unique constraint does the dedupe; RETURNING gives back only the new rows.
    stmt = (
        insert(Job)
        .values(rows)
        .on_conflict_do_nothing(index_elements=["content_hash"])
        .returning(Job.id)
    )
    inserted_ids = db.execute(stmt).scalars().all()
    return len(inserted_ids)


def run_source(db: Session, fetcher: Fetcher) -> IngestRun:
    """Fetch + save one source, and log the result in ingest_runs."""
    run = IngestRun(source=fetcher.source)
    db.add(run)
    db.commit()  # save the "started" row now, so even a crash leaves a trace

    try:
        jobs = fetcher.fetch()
        inserted = save_jobs(db, jobs)
        run.fetched = len(jobs)
        run.inserted = inserted
        run.duplicates = len(jobs) - inserted
        run.ok = True
    except Exception as exc:  # one broken source must not stop the others
        db.rollback()
        run.ok = False
        run.error = f"{type(exc).__name__}: {exc}"[:2000]

    run.finished_at = datetime.now(UTC)
    db.commit()
    return run


def main() -> None:
    with SessionLocal() as db:
        for fetcher in ALL_FETCHERS:
            run = run_source(db, fetcher)
            if run.ok:
                print(
                    f"{run.source:<10} fetched={run.fetched:<4} "
                    f"inserted={run.inserted:<4} duplicates={run.duplicates}"
                )
            else:
                print(f"{run.source:<10} FAILED: {run.error}")


# Runs only when started as a program (python -m app.ingest), not when imported
if __name__ == "__main__":
    main()
