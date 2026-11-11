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
