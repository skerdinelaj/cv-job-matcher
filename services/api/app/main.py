"""The FastAPI app. Run with:  uvicorn app.main:app --reload"""

from typing import Annotated

from fastapi import Depends, FastAPI
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.db import get_db

app = FastAPI(title="JobMatch API")

# A type alias: "a Session that FastAPI gets from get_db()".
# FastAPI calls get_db for each request and passes the result in (dependency injection).
DbSession = Annotated[Session, Depends(get_db)]


@app.get("/health")
def health(db: DbSession) -> dict[str, str]:
    """Is the API up, and can it talk to the database?"""
    db.execute(text("SELECT 1"))  # fails with an error if Postgres is unreachable
    return {"status": "ok", "database": "ok"}
