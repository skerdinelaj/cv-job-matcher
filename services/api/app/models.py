"""Database tables as Python classes (SQLAlchemy 2 typed style).

`Mapped[str]` = NOT NULL column, `Mapped[str | None]` = nullable column.
More tables are added in later steps, each with its own migration.
"""

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base


class Job(Base):
    """One job posting, normalised from any source."""

    __tablename__ = "jobs"

    id: Mapped[int] = mapped_column(primary_key=True)
    source: Mapped[str] = mapped_column(String(50))  # e.g. "arbeitnow", "remoteok"
    source_id: Mapped[str | None] = mapped_column(String(255))  # the job's id at the source
    url: Mapped[str] = mapped_column(Text)  # original posting; the UI links back to it
    title: Mapped[str] = mapped_column(Text)
    company: Mapped[str | None] = mapped_column(Text)
    location: Mapped[str | None] = mapped_column(Text)
    description: Mapped[str] = mapped_column(Text, default="")
    posted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    # server_default: Postgres fills in the time itself when we insert a row
    fetched_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    # A fingerprint of the job's content. UNIQUE = the database refuses duplicates.
    content_hash: Mapped[str] = mapped_column(String(64), unique=True)


class IngestRun(Base):
    """One run of one fetcher: how many jobs it found, inserted, skipped, and errors."""

    __tablename__ = "ingest_runs"

    id: Mapped[int] = mapped_column(primary_key=True)
    source: Mapped[str] = mapped_column(String(50))
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    fetched: Mapped[int] = mapped_column(Integer, default=0)
    inserted: Mapped[int] = mapped_column(Integer, default=0)
    duplicates: Mapped[int] = mapped_column(Integer, default=0)
    ok: Mapped[bool] = mapped_column(default=False)
    error: Mapped[str | None] = mapped_column(Text)


class JobEnrichment(Base):
    """What the LLM extracted from one job posting (one row per job)."""

    __tablename__ = "job_enrichment"

    # job_id is both the primary key and a link to jobs.id: at most one enrichment per job.
    # ondelete=CASCADE: if a job is deleted, its enrichment goes too.
    job_id: Mapped[int] = mapped_column(
        ForeignKey("jobs.id", ondelete="CASCADE"), primary_key=True
    )
    skills: Mapped[list[str]] = mapped_column(ARRAY(Text), default=list)
    must_have: Mapped[list[str]] = mapped_column(ARRAY(Text), default=list)
    nice_to_have: Mapped[list[str]] = mapped_column(ARRAY(Text), default=list)
    seniority: Mapped[str | None] = mapped_column(String(20))
    years_required: Mapped[int | None] = mapped_column(Integer)
    languages_required: Mapped[list[str]] = mapped_column(ARRAY(Text), default=list)
    location_rule: Mapped[str] = mapped_column(String(30))  # worldwide/europe/country_restricted/unclear
    apply_email: Mapped[str | None] = mapped_column(Text)  # only if written in the posting
    salary_text: Mapped[str | None] = mapped_column(Text)
    enriched_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    model: Mapped[str] = mapped_column(String(100))  # which LLM produced this


class LLMCall(Base):
    """A log row for every LLM call: for cost tracking and debugging."""

    __tablename__ = "llm_calls"

    id: Mapped[int] = mapped_column(primary_key=True)
    step: Mapped[str] = mapped_column(String(50))  # e.g. "enrich", "judge", "draft"
    model: Mapped[str] = mapped_column(String(100))
    input_tokens: Mapped[int | None] = mapped_column(Integer)
    output_tokens: Mapped[int | None] = mapped_column(Integer)
    latency_ms: Mapped[int] = mapped_column(Integer)
    ok: Mapped[bool]
    error: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
