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
