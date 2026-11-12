"""decode html entities in job title company location

A DATA migration (changes rows, not tables). Some saved jobs have "&amp;" instead of "&"
in title/company/location. The fetchers now decode these, so the same job would get a
NEW content_hash on the next ingest and be inserted twice. Here we clean the saved rows
and recompute their content_hash, so they stay recognised as the same job.

Revision ID: 69d783692cbf
Revises: e80b6e2b3bd8
Create Date: 2026-11-12 17:01:20.898788
"""

import hashlib
import html
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "69d783692cbf"
down_revision: str | None = "e80b6e2b3bd8"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


# Copies of the app's logic AT THIS POINT IN TIME. A migration must not import app code:
# if app code changes later, an old migration must still do exactly what it did today.
def _clean(value: str | None) -> str | None:
    return None if value is None else " ".join(html.unescape(value).split())


def _content_hash(company: str | None, title: str) -> str:
    def norm(text: str) -> str:
        return " ".join(text.lower().split())

    key = f"{norm(company or '')}|{norm(title)}"
    return hashlib.sha256(key.encode("utf-8")).hexdigest()


def upgrade() -> None:
    conn = op.get_bind()
    rows = conn.execute(
        sa.text(
            "SELECT id, title, company, location FROM jobs "
            "WHERE title ~ '&[#a-zA-Z0-9]+;' OR company ~ '&[#a-zA-Z0-9]+;' "
            "OR location ~ '&[#a-zA-Z0-9]+;'"
        )
    ).all()

    for row in rows:
        title, company, location = _clean(row.title), _clean(row.company), _clean(row.location)
        new_hash = _content_hash(company, title or "")

        # Rare case: the clean version of this job is already saved -> this row is a duplicate.
        clash = conn.execute(
            sa.text("SELECT id FROM jobs WHERE content_hash = :h AND id <> :id"),
            {"h": new_hash, "id": row.id},
        ).first()
        if clash:
            conn.execute(sa.text("DELETE FROM jobs WHERE id = :id"), {"id": row.id})
            continue

        conn.execute(
            sa.text(
                "UPDATE jobs SET title = :t, company = :c, location = :l, content_hash = :h "
                "WHERE id = :id"
            ),
            {"t": title, "c": company, "l": location, "h": new_hash, "id": row.id},
        )


def downgrade() -> None:
    # Nothing to undo: putting "&amp;" back would only re-create the bug.
    pass
