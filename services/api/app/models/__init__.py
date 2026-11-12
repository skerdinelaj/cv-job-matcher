"""All database tables, grouped by topic in this folder.

Importing them here means:
  - the rest of the app can write `from app.models import Job` (no need to know the file),
  - Alembic sees every table when it compares models with the database.
When you add a table in a new file, import it here too.
"""

from app.models.jobs import Job, JobEnrichment
from app.models.logs import IngestRun, LLMCall

__all__ = ["IngestRun", "Job", "JobEnrichment", "LLMCall"]
