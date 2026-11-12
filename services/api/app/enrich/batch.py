"""Send several jobs to the LLM in ONE request, and map the answers back to each job."""

from app.core.llm import LLM
from app.enrich.prompts import SYSTEM_PROMPT, build_batch_prompt
from app.enrich.schema import EnrichBatch, JobProfile
from app.models import Job

BATCH_SIZE = 8  # jobs per LLM request (free tier: ~20 requests/day)


def make_batches(jobs: list[Job], size: int = BATCH_SIZE) -> list[list[Job]]:
    """[1..20] with size 8 -> [[1..8], [9..16], [17..20]]"""
    return [jobs[i : i + size] for i in range(0, len(jobs), size)]


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
