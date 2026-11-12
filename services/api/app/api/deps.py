"""Shared FastAPI dependencies for all route files."""

from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from app.core.db import get_db

# A type alias: "a Session that FastAPI gets from get_db()".
# FastAPI calls get_db for each request and passes the result in (dependency injection).
DbSession = Annotated[Session, Depends(get_db)]
