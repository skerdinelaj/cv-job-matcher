"""The "form" the LLM fills in for each job (Pydantic classes = JSON schemas).

The Field descriptions are sent to Gemini as part of the schema, so they are
instructions too.
"""

from typing import Literal

from pydantic import BaseModel, Field

LocationRule = Literal["worldwide", "europe", "country_restricted", "unclear"]


class JobProfile(BaseModel):
    """Structured facts about one job posting."""

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
    location_rule: LocationRule
    apply_email: str | None = Field(
        description="An email address for applications, ONLY if written in the posting."
    )
    salary_text: str | None = Field(description="Salary exactly as written, else null.")


class BatchItem(JobProfile):
    """One job's profile inside a batch answer: the same form plus which job it is."""

    job_id: int = Field(description="The id of the job, copied from 'JOB id=...'.")


class EnrichBatch(BaseModel):
    """What one LLM request returns: one profile per job in the batch."""

    jobs: list[BatchItem]
