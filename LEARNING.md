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

## Refactor: folder structure (where everything lives)
**The idea:** We moved the code into one folder per pipeline step (`ingest/`, `enrich/`, later `embed/`, `match/`, `draft/`...) plus a few shared folders. Nothing changed in what the code does; only where it lives.

**The map (`services/api/app/`):**
- `main.py`: creates the FastAPI app and plugs in the routes from `api/`.
- `core/`: plumbing used everywhere: `config.py` (settings from `.env`), `db.py` (database connection), `llm.py` (the one LLM gateway).
- `models/`: database tables by topic: `jobs.py` (Job, JobEnrichment), `logs.py` (IngestRun, LLMCall). `__init__.py` imports them all.
- `shared/`: small pure helpers: `text.py`, `skills.py`.
- `ingest/` (Step A, `python -m app.ingest`): `run.py` (the loop), `dedupe.py` (content_hash), `fetchers/` (one file per source).
- `enrich/` (Step B, `python -m app.enrich`): `run.py` (the loop), `schema.py` (the form), `prompts.py`, `prefilter.py`, `batch.py`, `guardrails.py`.
- `api/`: HTTP routes, one file per area (`health.py` now), plus `deps.py` (shared `DbSession`).

**Rule of thumb:** "Which step is this for?" → that step's folder. "Is it used by many steps?" → `core/` (plumbing) or `shared/` (small helpers). "Is it a table?" → `models/`.

**Like in JavaScript:**
- Feature folders ≈ grouping by feature in a Next.js/React app instead of by file type.
- `models/__init__.py` re-exporting tables ≈ an `index.ts` barrel file.
- `__main__.py` ≈ the `"main"`/`bin` entry of a package: `python -m app.enrich` runs it.
- FastAPI `APIRouter` ≈ `express.Router()`.

**Why this way:** Each file has one job and a name that says it, so I can find things fast. Trade-off: more files, and you jump between them a bit more.

**Words to know:**
- **Package:** a folder of Python files with an `__init__.py`; you import from it like a module.
- **`__main__.py`:** the file Python runs when you run a package with `python -m`.
- **Refactor:** changing how code is organised without changing what it does.
- **Router:** a group of related API routes that the app plugs in.

## Step W0: Angular setup
**The idea:** We created the Angular app in `apps/web` with the Angular CLI. Angular comes with everything built in (router, HTTP client, tests, build), so there are fewer libraries to pick than in React. We also set up a dev proxy, so the app calls `/api/...` on its own address and the dev server forwards it to FastAPI.

**What we built:**
- `apps/web/` (created by `ng new`): the Angular 22 app: standalone, zoneless, SCSS, Vitest, no SSR.
- `src/main.ts`: starts the app with `bootstrapApplication(App, appConfig)`.
- `src/app/app.config.ts`: the app-wide "providers" (router, error listeners), like the providers you wrap around `<App />` in React.
- `src/app/app.ts` + `app.html` + `app.scss`: the root component, split into logic, template and styles.
- `src/app/app.routes.ts`: the list of routes (empty for now).
- `proxy.conf.json`: sends `/api/*` to `http://localhost:8000` and removes the `/api` prefix (`/api/health` → `/health`).
- `angular.json`: the project config (build, serve, test). We added `proxyConfig` so `ng serve` uses the proxy.
- `src/app/core/`, `shared/`, `features/*`: empty feature folders for the next steps.

**Like in React:**
- `ng new` ≈ `npm create vite@latest`, but with router, HTTP and tests already included.
- `ng serve` ≈ `npm run dev`. `ng build` ≈ `npm run build`. `ng test` ≈ `vitest`.
- `bootstrapApplication(App, appConfig)` ≈ `createRoot(el).render(<Providers><App /></Providers>)`.
- `proxy.conf.json` ≈ `server.proxy` in `vite.config.ts`.
- `ng generate component x` ≈ copying a component file by hand, but the CLI does it with the test file included.

**Old way:** Apps started with `platformBrowserDynamic().bootstrapModule(AppModule)`, where `AppModule` was an `@NgModule` that declared every component, and zone.js was required.

**Why this way:** A dev proxy means the browser talks to only one address, so we need no CORS setup, and production with nginx works the same way. Trade-off: the proxy works only in `ng serve`, so production needs its own forwarding (nginx, later).

**Interview line:** "The Angular app calls a relative `/api` path; in dev the Angular dev server proxies it to FastAPI and in production nginx does, so there's no CORS and no hard-coded backend URL in the frontend."

**Words to know:**
- **Angular CLI (`ng`):** the command-line tool that creates, runs, tests, builds and generates Angular code.
- **Standalone component:** a component that lists its own imports; no NgModule needed.
- **Zoneless:** Angular updates the page when signals change, without zone.js watching every click and timer.
- **OnPush:** a component is re-checked only when its inputs or the signals it reads change. It's the default for new components in Angular 22.
- **Provider:** something registered with Angular so it can be injected where needed (like a value in a React Context).
- **Proxy:** a server in the middle that forwards requests to another server.
- **CORS:** a browser rule that blocks calls to a different address unless that server allows them.

**Check yourself:** If the Angular app calls `/api/matches`, which URL does FastAPI actually receive, and why?

## Step W1: Components and templates
**The idea:** An Angular component is a class (the logic) plus a template (the HTML) plus styles. A parent passes data down with inputs and listens to events with outputs, like props and callback props in React. Templates use `@if`, `@for` and `@switch` blocks, and pipes format values right inside `{{ }}`.

**What we built:**
- `features/today/match.model.ts`: a temporary `Match` type shaped like the planned `GET /matches` response (replaced by generated types in W3).
- `features/today/mock-matches.ts`: 3 fake matches to build the UI before the API exists.
- `shared/pipes/score-label.pipe.ts`: a custom pipe: `{{ 91 | scoreLabel }}` → "Strong match".
- `features/today/match-card/`: one card per match: `input.required<Match>()`, a `skip` output, `ngOnInit`/`ngOnDestroy` logs.
- `features/today/today-page.*`: the list of cards with `@for … @empty`; Skip hides a card (UI only for now).
- `app.ts`/`app.html`: the top bar + the Today page (the router replaces this in W3).

**Like in React:**
- `readonly match = input.required<Match>()` ≈ `function MatchCard({ match }: { match: Match })`. You read it as `match()`.
- `readonly skip = output<number>()` + `this.skip.emit(id)` ≈ an `onSkip(id)` callback prop.
- `<app-match-card [match]="m" (skip)="onSkip($event)" />` ≈ `<MatchCard match={m} onSkip={onSkip} />`.
- `@for (m of matches(); track m.id) {…} @empty {…}` ≈ `matches.length ? matches.map(m => <X key={m.id} />) : <Empty />`.
- `@if (a) {…} @else {…}` ≈ `{a ? <A /> : <B />}`.
- `@let job = match().job;` ≈ `const job = match.job;` at the top of a component.
- `[class.score--strong]="score >= 85"` ≈ `className={clsx({ 'score--strong': score >= 85 })}`.
- Pipe `{{ date | date: 'd MMM' }}` ≈ calling `format(date, 'd MMM')` inside JSX.
- `ngOnInit` + `ngOnDestroy` ≈ `useEffect(() => { … ; return () => cleanup }, [])`.
- Component `.scss` scoped to the component ≈ CSS Modules.

**Old way:** `@Input() match!: Match;` and `@Output() skip = new EventEmitter<number>();` with `*ngIf="..."`, `*ngFor="let m of matches; trackBy: fn"` and `[ngSwitch]`, and the component declared in an NgModule.

**Why this way:** The card only displays data and emits events; the page owns the list. This "presentational vs container" split keeps the card reusable and easy to test. Trade-off: one more file and passing data through inputs instead of reading it directly.

**Interview line:** "I split the Today page into a container that owns the state and a presentational card with signal inputs and outputs, using the new control-flow blocks and a pure custom pipe for display logic."

**Words to know:**
- **Template:** the HTML of a component, with Angular syntax for data and events.
- **Interpolation `{{ }}`:** shows a value as text.
- **Property binding `[x]="..."`:** sets an element property or a component input from an expression.
- **Event binding `(x)="..."`:** runs code when an event (or a component output) fires; `$event` is its value.
- **Control flow (`@if`, `@for`, `@switch`):** template blocks for conditions, lists and switches.
- **`track`:** the unique key for each `@for` item, so Angular updates only the items that changed.
- **Pipe:** a small function used in templates to format a value; "pure" pipes run again only when the input changes.
- **Lifecycle hook:** a method Angular calls at a set moment (`ngOnInit` after inputs are set, `ngOnDestroy` before removal).
- **`:host`:** in component styles, the component's own element (`<app-match-card>`).
- **`ng test --watch=false`:** runs the unit tests once and exits (without the flag it re-runs on every save).
- **`ng build`:** makes the production version in `dist/`; stricter than `ng serve`. Run test + build before each commit.

**Check yourself:** Why do we log `this.match().id` in `ngOnInit` and not in the constructor?
