"""Database tables as Python classes (SQLAlchemy 2 typed style).

`Mapped[str]` = NOT NULL column, `Mapped[str | None]` = nullable column.
More tables are added in later steps, each with its own migration.
"""

from datetime import datetime

from sqlalchemy import DateTime, Integer, String, Text, func
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
