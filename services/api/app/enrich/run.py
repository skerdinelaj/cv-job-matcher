"""Step B of the pipeline: read each new job ONCE and store structured facts.

Run from services/api:  python -m app.enrich

For every job without a job_enrichment row:
  1. prefilter.py  - obvious cases are decided in code, without the LLM.
  2. batch.py      - the rest go to the LLM, several jobs per request.
  3. guardrails.py - every LLM answer is checked before it's saved.
"""

import argparse
import logging

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.db import SessionLocal
from app.core.llm import DailyQuotaExhaustedError, GeminiLLM
from app.enrich.batch import BATCH_SIZE, enrich_batch, make_batches
from app.enrich.guardrails import clean_profile
from app.enrich.prefilter import PREFILTER_MODEL, prefilter
from app.enrich.schema import JobProfile
from app.models import Job, JobEnrichment


def jobs_to_enrich(db: Session, limit: int) -> list[Job]:
    """Jobs with NO enrichment row yet (LEFT JOIN ... WHERE enrichment IS NULL)."""
    stmt = (
        select(Job)
        .outerjoin(JobEnrichment, JobEnrichment.job_id == Job.id)
        .where(JobEnrichment.job_id.is_(None))
        .order_by(Job.id)
        .limit(limit)
    )
    return list(db.scalars(stmt))


def save(db: Session, job: Job, profile: JobProfile, model: str) -> JobEnrichment:
    enrichment = JobEnrichment(job_id=job.id, model=model, **profile.model_dump())
    db.add(enrichment)
    return enrichment


def _print(job: Job, e: JobEnrichment) -> None:
    print(
        f"[{job.id}] {job.title[:45]:<45} | {e.location_rule:<18} | "
        f"must={len(e.must_have)} langs={e.languages_required} email={e.apply_email}"
        f"{'  (prefilter)' if e.model == PREFILTER_MODEL else ''}"
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Enrich new jobs (pre-filter + LLM batches).")
    parser.add_argument("--limit", type=int, default=200, help="max jobs to enrich this run")
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    # Hide the libraries' chatty INFO lines (every HTTP request, "AFC is enabled")
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("google_genai").setLevel(logging.WARNING)

    with SessionLocal() as db:
        jobs = jobs_to_enrich(db, args.limit)

        # 1. Pre-filter: no LLM needed
        for_llm: list[Job] = []
        for job in jobs:
            decided = prefilter(job)
            if decided is None:
                for_llm.append(job)
                continue
            _print(job, save(db, job, decided, PREFILTER_MODEL))
        db.commit()
        print(f"\nPre-filter decided {len(jobs) - len(for_llm)} job(s). LLM needed for {len(for_llm)}.")
        if not for_llm:
            return

        # 2. LLM in batches
        llm = GeminiLLM()
        batches = make_batches(for_llm)
        print(f"Sending {len(batches)} batch(es) of up to {BATCH_SIZE} to {llm.model}\n")
        for batch in batches:
            try:
                profiles = enrich_batch(batch, llm)
            except DailyQuotaExhaustedError as exc:
                print(f"STOPPED: {exc} The remaining jobs will be done on the next run.")
                break
            except Exception as exc:  # one bad batch must not stop the rest
                print(f"Batch {[j.id for j in batch]} FAILED: {type(exc).__name__}: {str(exc)[:200]}")
                continue

            # 3. Guard-rails, then save
            for job in batch:
                profile = profiles.get(job.id)
                if profile is None:  # the LLM skipped it: it stays un-enriched, retried next run
                    print(f"[{job.id}] missing from the LLM answer, will retry next run")
                    continue
                _print(job, save(db, job, clean_profile(profile, job), llm.model))
            db.commit()  # commit per batch: a later failure doesn't lose earlier work
