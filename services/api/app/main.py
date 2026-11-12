"""The FastAPI app. Run with:  uvicorn app.main:app --reload

This file only creates the app and plugs in the routers from app/api/.
Each area (health, cvs, drafts, ...) has its own file there.
"""

from fastapi import FastAPI

from app.api import health

app = FastAPI(title="JobMatch API")

app.include_router(health.router)
