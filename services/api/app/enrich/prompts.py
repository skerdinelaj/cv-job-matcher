"""The text we send to the LLM for enrichment: the rules + the jobs."""

from app.models import Job

MAX_DESCRIPTION_CHARS = 4000  # per job, so a batch stays a reasonable size

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


def build_batch_prompt(jobs: list[Job]) -> str:
    """All jobs of one batch in one text, each marked with its id."""
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
