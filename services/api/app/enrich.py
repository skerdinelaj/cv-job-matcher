"""Step B of the pipeline: read each new job ONCE and store structured facts.

Run from services/api:  python -m app.enrich --limit 200

For every job without a job_enrichment row:
  1. Pre-filter in code (app/prefilter.py): obvious cases are decided without the LLM.
  2. The rest go to the LLM in BATCHES (several jobs per request) to save daily quota.
  3. Guard-rails in code clean every answer before it's saved.
"""

import argparse
import logging
import re
from typing import Literal

from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db import SessionLocal
from app.llm import LLM, DailyQuotaExhaustedError, GeminiLLM
from app.models import Job, JobEnrichment
from app.prefilter import detect_german, location_is_outside_reach
from app.skills import normalise_skills

logger = logging.getLogger(__name__)

BATCH_SIZE = 8  # jobs per LLM request
MAX_DESCRIPTION_CHARS = 4000  # per job, so a batch stays a reasonable size
PREFILTER_MODEL = "prefilter"  # stored in job_enrichment.model when code decided, not the LLM


# --- The "form" the LLM fills in for each job. Descriptions are sent to Gemini too. ---
class JobProfile(BaseModel):
    skills: list[str] = Field(description="All technical skills/tools mentioned in the posting.")
    must_have: list[str] = Field(description="Skills the posting says are required.")
    nice_to_have: list[str] = Field(description="Skills the posting says are a plus/bonus.")
    seniority: Literal["intern", "junior", "mid", "senior", "lead", "principal"] | None = Field(
        description="Seniority level if stated or clear from the title, else null."
    )
    years_required: int | None = Field(
        description="Minimum years of experience if a number is stated, else null."
    )
    languages_required: list[str] = Field(
        description="Human languages the candidate MUST speak (e.g. English, German). "
        "Not programming languages."
    )
    location_rule: Literal["worldwide", "europe", "country_restricted", "unclear"]
    apply_email: str | None = Field(
        description="An email address for applications, ONLY if written in the posting."
    )
    salary_text: str | None = Field(description="Salary exactly as written, else null.")


class BatchItem(JobProfile):
    job_id: int = Field(description="The id of the job, copied from 'JOB id=...'.")


class EnrichBatch(BaseModel):
    """What one LLM request returns: one profile per job in the batch."""

    jobs: list[BatchItem]


SYSTEM_PROMPT = """You extract facts from job postings into JSON.
You get several jobs. Return exactly one entry per job, with its job_id.
Rules:
- Use ONLY what each posting says. If something is not stated, use null or an empty list. Never guess.
- Never mix up jobs: each entry must use only its own posting.
- Skills: short names (e.g. "React", "PostgreSQL"), no sentences.
- languages_required: only spoken languages that are required. If the posting is written in
  a language other than English and expects you to work in it, include that language.
- location_rule, for a candidate living in Albania (Europe, NOT in the EU):
  - "worldwide": the posting explicitly says anywhere / worldwide / any country.
    ("Fully remote" alone does NOT say where: that is "unclear".)
  - "europe": open to Europe, EMEA, or CET/European time zones, or Albania is listed.
  - "country_restricted": only specific countries or regions that do not include Albania
    (e.g. "USA only", "remote within Germany", "EU only", "EU work permit required"), or on-site.
  - "unclear": the posting does not say where candidates can be.
- apply_email: copy it exactly as written. If no email is written, null. Never build one."""


# --- 1. Pre-filter --------------------------------------------------------------------
def prefilter(job: Job) -> JobProfile | None:
    """Decide obvious jobs in code. Returns a profile, or None = "ask the LLM"."""
    if location_is_outside_reach(job.location):
        return _empty_profile(location_rule="country_restricted")
    if detect_german(job.description):
        # Posting written in German -> German is needed. I don't speak it, so the
        # language filter in matching will drop it. We don't extract skills for it.
        return _empty_profile(location_rule="unclear", languages=["German"])
    return None


def _empty_profile(location_rule: str, languages: list[str] | None = None) -> JobProfile:
    return JobProfile.model_validate(
        {
            "skills": [], "must_have": [], "nice_to_have": [], "seniority": None,
            "years_required": None, "languages_required": languages or [],
            "location_rule": location_rule, "apply_email": None, "salary_text": None,
        }
    )  # fmt: skip


# --- 2. LLM in batches ------------------------------------------------------------------
def build_batch_prompt(jobs: list[Job]) -> str:
    blocks = []
    for job in jobs:
        blocks.append(
            f"=== JOB id={job.id} ===\n"
            f"Title: {job.title}\n"
            f"Company: {job.company or 'unknown'}\n"
            f"Location field: {job.location or 'not given'}\n"
            f"Description:\n{job.description[:MAX_DESCRIPTION_CHARS]}"
        )
    return "\n\n".join(blocks)


def enrich_batch(jobs: list[Job], llm: LLM) -> dict[int, JobProfile]:
    """One LLM request for several jobs. Returns {job_id: profile} for jobs it answered."""
    result = llm.generate_json(
        step="enrich",
        prompt=build_batch_prompt(jobs),
        schema=EnrichBatch,
        system=SYSTEM_PROMPT,
        # Copying facts from text needs almost no reasoning. We tested minimal vs low vs
        # default on the same 5 jobs: same quality, ~5x fewer output tokens than default.
        thinking="minimal",
    )
    asked = {job.id for job in jobs}
    profiles: dict[int, JobProfile] = {}
    for item in result.jobs:
        # Ignore ids we didn't ask about, and duplicates (keep the first)
        if item.job_id in asked and item.job_id not in profiles:
            profiles[item.job_id] = JobProfile.model_validate(item.model_dump(exclude={"job_id"}))
    return profiles


# --- 3. Guard-rails -----------------------------------------------------------------------
_EMAIL_SHAPE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def clean_profile(profile: JobProfile, job: Job) -> JobProfile:
    """Guard-rails in code: don't trust the LLM blindly."""
    # 1. Languages: "english " -> "English", no duplicates
    profile.languages_required = sorted({lang.strip().title() for lang in profile.languages_required})

    # 2. Skill names: one spelling each. Spoken languages ("German") are not skills:
    #    the LLM sometimes puts them in must_have, so we remove them there.
    languages = {lang.lower() for lang in profile.languages_required}

    def only_skills(names: list[str]) -> list[str]:
        return [s for s in normalise_skills(names) if s.lower() not in languages]

    profile.skills = only_skills(profile.skills)
    profile.must_have = only_skills(profile.must_have)
    profile.nice_to_have = only_skills(profile.nice_to_have)

    # 3. apply_email must look like an email AND really appear in the posting text.
    #    (Never guess or build an email address.)
    if profile.apply_email:
        email = profile.apply_email.strip()
        if not _EMAIL_SHAPE.match(email) or email.lower() not in job.description.lower():
            logger.info("Dropped apply_email %r for job %s: not in posting", email, job.id)
            profile.apply_email = None
        else:
            profile.apply_email = email

    return profile


# --- Database helpers + main ----------------------------------------------------------------
def save(db: Session, job: Job, profile: JobProfile, model: str) -> JobEnrichment:
    enrichment = JobEnrichment(job_id=job.id, model=model, **profile.model_dump())
    db.add(enrichment)
    return enrichment


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
        batches = [for_llm[i : i + BATCH_SIZE] for i in range(0, len(for_llm), BATCH_SIZE)]
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

            for job in batch:
                profile = profiles.get(job.id)
                if profile is None:  # the LLM skipped it: it stays un-enriched, retried next run
                    print(f"[{job.id}] missing from the LLM answer, will retry next run")
                    continue
                _print(job, save(db, job, clean_profile(profile, job), llm.model))
            db.commit()  # commit per batch: a later failure doesn't lose earlier work


if __name__ == "__main__":
    main()
