# What I learned building JobMatch

One entry per step, in simple words.

## Step 0: Project skeleton
**The idea:** Before writing features, we set up the empty project: folders, a list of files git must ignore, a settings template, and a database running in Docker. We also asked Google which AI models our key can use, because Google renames models often and guessing a name breaks the app.

**What we built:**
- `.gitignore`: tells git to never save secrets (`.env`), my real CV (`data/private/`), or installed packages.
- `.env.example`: a template of all settings with no secrets. I copy it to `.env` and fill in real values.
- `docker-compose.yml`: starts PostgreSQL 16 with pgvector (a Postgres add-on that stores and searches vectors) in Docker, on port 5433.
- `services/api/requirements.txt`: the Python packages this project needs.
- `services/api/scripts/list_models.py`: prints the Gemini models my key can use, split into chat and embedding models.
- `LEARNING.md`: this file.

**Like in JavaScript:**
- `requirements.txt` ≈ the `dependencies` in `package.json`.
- `pip install -r requirements.txt` ≈ `npm install`.
- `.venv` (virtual environment) ≈ `node_modules`: packages installed only for this project.
- `python-dotenv` ≈ the `dotenv` npm package.

**Why this way:** Model names live in ONE place (`.env`), so when Google retires a model I change one line, not code. The trade-off: I must remember to update `.env.example` when I add a new setting.

**Interview line:** "I kept secrets out of git from day one and made the model names configuration, not code, because LLM providers retire model names often."

**Words to know:**
- **Virtual environment (venv):** a private folder of Python packages for one project, so projects don't clash.
- **Docker container:** a small isolated "box" that runs a program (here Postgres) the same way on any machine.
- **Port:** a numbered door on my computer; only one program can use each door. 5432 was taken, so we use 5433.
- **Embedding:** a list of numbers that represents the meaning of a text, so similar texts get similar numbers.
- **pgvector:** a Postgres add-on that stores embeddings and finds the most similar ones quickly.

## Step 1: FastAPI + database + first migration
**The idea:** We now have a small web API (FastAPI) that can talk to the database. Tables are written as Python classes, and a migration tool (Alembic) turns those classes into real tables in Postgres. A `/health` endpoint proves the API and the database are both working.

**What we built:**
- `services/api/app/config.py`: reads `.env` into one typed `settings` object, so a missing or wrong setting fails at startup.
- `services/api/app/db.py`: the connection pool (engine), sessions, the `Base` class for tables, and `get_db()` that gives each request its own session.
- `services/api/app/models.py`: the `jobs` and `ingest_runs` tables as Python classes.
- `services/api/app/main.py`: the FastAPI app with `GET /health`.
- `services/api/alembic.ini`, `alembic/env.py`, `alembic/script.py.mako`: Alembic setup. It reads the database URL from `.env`.
- `services/api/alembic/versions/..._create_jobs_and_ingest_runs.py`: the first migration, written by Alembic and checked by me.

**Like in JavaScript:**
- FastAPI ≈ Express: `@app.get("/health")` ≈ `app.get("/health", handler)`.
- SQLAlchemy ≈ Prisma/TypeORM: a class = a table.
- Alembic ≈ Prisma Migrate: `alembic revision --autogenerate` ≈ `prisma migrate dev`, `alembic upgrade head` ≈ `prisma migrate deploy`.
- `pydantic-settings` ≈ validating `process.env` with zod.
- `Depends(get_db)` ≈ a middleware that attaches a database connection to each request.
- `uvicorn --reload` ≈ `nodemon`.

**Why this way:** Migrations are versioned files in git, so anyone (or CI) can rebuild the exact same database. The trade-off: autogenerate can miss or guess wrong, so I always read the migration before applying it.

**Interview line:** "Schema changes go through reviewed Alembic migrations, and constraints like unique `content_hash` live in the database, so duplicates are impossible even if the code has a bug."

**Words to know:**
- **ORM:** a library that lets you use database tables as classes and objects instead of writing raw SQL.
- **Migration:** a versioned script that changes the database structure (create a table, add a column), with an undo (`downgrade`).
- **Session:** one conversation with the database; you add or change things, then `commit` to save them.
- **Engine / connection pool:** a set of open database connections that get reused, because opening a new one each time is slow.
- **Dependency injection:** FastAPI creates what your endpoint needs (here a session) and passes it in for you.
- **Type hint:** `Mapped[str | None]` tells Python (and SQLAlchemy) the type; here it also decides NOT NULL vs nullable.
- **Unique constraint:** a database rule that refuses two rows with the same value in a column.

## Step 2: Fetchers + dedupe + ingest runs
**The idea:** Each job site sends its data in its own format. A small "fetcher" for each site downloads the JSON and converts it into one shared shape (`RawJob`). Then we save the jobs, and the database itself refuses jobs we already have, so running the command twice adds nothing new.

**What we built:**
- `app/text.py`: helpers to turn HTML into plain text, repair broken characters (`â€”` → `—`), and lowercase text for the fingerprint.
- `app/fetchers/base.py`: `RawJob` (the shared job shape) and `Fetcher` (the base class: `fetch()` = `download()` + `parse()`).
- `app/fetchers/arbeitnow.py`, `remoteok.py`, `remotive.py`: one small fetcher per site; each only writes `parse()`.
- `app/fetchers/__init__.py`: `ALL_FETCHERS`, the list of sources.
- `app/ingest.py`: `python -m app.ingest`. For each source: log a run, fetch, insert with `ON CONFLICT DO NOTHING`, count new vs duplicate, save the result in `ingest_runs`.
- `tests/fixtures/*.json`: 3 real sample jobs per source, for tests later.

**Like in JavaScript:**
- `httpx.get(...)` ≈ `fetch(...)` / axios; `raise_for_status()` ≈ `if (!res.ok) throw ...`.
- Pydantic `RawJob` ≈ a TypeScript interface that is also checked at runtime (like zod).
- `Fetcher` base class with `parse()` ≈ an interface every adapter implements (the adapter pattern).
- `if __name__ == "__main__":` ≈ code that runs only when you call `node file.js`, not when you import it.

**Why this way:** The duplicate check lives in the database (a unique `content_hash` + `ON CONFLICT DO NOTHING`), so it's always enforced and costs one query. The trade-off: the fingerprint is company + title, so one company posting the same title for two countries counts as one job.

**Interview line:** "Every source is a small adapter with the same interface, `parse()` is pure so it's tested on saved fixtures, and dedupe is enforced by a unique constraint, which makes the ingest safe to re-run."

**Words to know:**
- **Fetcher / adapter:** a small piece of code that converts one outside format into our own format.
- **Normalise:** convert different formats into one standard shape.
- **Hash (SHA-256):** a fixed-length fingerprint of some text; the same text always gives the same hash.
- **Idempotent:** running it twice gives the same result as once (the second ingest added 0 jobs).
- **`ON CONFLICT DO NOTHING`:** Postgres: "if this row breaks a unique rule, skip it quietly instead of failing."
- **Fixture:** a saved sample of real data used in tests, so tests don't need the network.
- **Mojibake:** garbled characters caused by reading text with the wrong encoding.


### Fix: "&amp;" in job titles (data migration)
**The idea:** Some sources send `&amp;` instead of `&`. We now decode it in ONE place (a validator on `RawJob`), and a **data migration** cleaned the 6 rows already saved and recomputed their fingerprint, so the next ingest doesn't treat them as new jobs.
**Like in JavaScript:** a Pydantic `field_validator` ≈ a zod `.transform()` on a field.
**Words to know:**
- **Data migration:** a migration that changes rows (data), not tables (structure).
- **HTML entity:** a code like `&amp;` that means `&` inside HTML.
- **Why the migration copies code instead of importing it:** a migration must do the same thing forever, even if the app code changes later.
