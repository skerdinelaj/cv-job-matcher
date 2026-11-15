"""GET /health: is the API up, and can it talk to the database?"""

from fastapi import APIRouter
from pydantic import BaseModel
from sqlalchemy import text

from app.api.deps import DbSession

# A router = a group of routes (like an Express Router). main.py plugs it into the app.
router = APIRouter(tags=["health"])


class HealthOut(BaseModel):
    """The response shape. FastAPI puts it in the OpenAPI schema (/openapi.json),
    and the Angular app generates its TypeScript type from there."""

    status: str
    database: str


@router.get("/health")
def health(db: DbSession) -> HealthOut:
    db.execute(text("SELECT 1"))  # fails with an error if Postgres is unreachable
    return HealthOut(status="ok", database="ok")
