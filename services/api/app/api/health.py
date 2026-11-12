"""GET /health: is the API up, and can it talk to the database?"""

from fastapi import APIRouter
from sqlalchemy import text

from app.api.deps import DbSession

# A router = a group of routes (like an Express Router). main.py plugs it into the app.
router = APIRouter(tags=["health"])


@router.get("/health")
def health(db: DbSession) -> dict[str, str]:
    db.execute(text("SELECT 1"))  # fails with an error if Postgres is unreachable
    return {"status": "ok", "database": "ok"}
