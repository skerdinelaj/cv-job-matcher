"""Database connection: the engine, sessions, and the Base class for models."""

from collections.abc import Iterator

from sqlalchemy import MetaData, create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.core.config import settings

# The engine holds a pool of connections to Postgres (create once, reuse everywhere).
# pool_pre_ping: check a connection is alive before using it.
engine = create_engine(settings.database_url, pool_pre_ping=True)

# A factory that makes Sessions. A Session = one "unit of work" with the database.
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)

# Predictable names for indexes and constraints, so Alembic migrations are stable.
# e.g. a unique constraint on jobs.content_hash is named "uq_jobs_content_hash".
NAMING_CONVENTION = {
    "ix": "ix_%(table_name)s_%(column_0_name)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}


class Base(DeclarativeBase):
    """Every table class inherits from this. Alembic reads Base.metadata."""

    metadata = MetaData(naming_convention=NAMING_CONVENTION)


def get_db() -> Iterator[Session]:
    """FastAPI dependency: open a session for one request, always close it after.

    `yield` hands the session to the endpoint; the code after it runs
    when the request is finished (like a `finally` block).
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
