# JobMatch: my personal job-search assistant (guided learning + portfolio project)

## Who I am and the goal
I'm Skerdi, a full-stack developer (5 years React/TypeScript) moving into AI engineering. I live in Albania and I'm looking for remote jobs. I'm still learning Python. I'm also learning Angular through this project's frontend. I learn best hands-on and guided, with short and simple explanations.

**The product (personal use only):** an app that automates my job search from start to finish, with me approving every application:
1. **Find**: every night, collect new jobs from free job APIs.
2. **Match**: score each job against my CV and keep the best ones.
3. **Prepare**: for each good match, draft a short tailored email and cover letter.
4. **Approve**: I see each draft on a page and click Send, Edit or Skip.
5. **Send**: send the email with my CV attached from my own Gmail.
6. **Track**: keep the status of every application and remind me to follow up.

It is also a **portfolio project for GitHub**: clean code, tests, CI, Docker, a strong README.

## The most important rule: I click Send
- **Nothing is ever sent automatically.** An email goes out only after I click Send on that specific draft in the UI. No "send all" button, no auto-send setting, no sending from scripts or tests.
- The send endpoint must require an explicit approved draft id, and must refuse a draft that is not in status `approved`.
- In development and tests, sending is OFF by default (`EMAIL_MODE=dry_run` prints the email instead). Real sending needs `EMAIL_MODE=live` in `.env`.
- Never send twice for the same job: enforce it in the database (unique constraint), not only in the UI.

## LEARNING.md (required)
Keep a file `LEARNING.md` in the project root. After EVERY completed step, add one entry, in the simplest words possible:

```
## Step N: <name>
**The idea:** 2-3 simple sentences. No jargon without explaining it.
**What we built:** which files, and what each does in one line.
**Like in JavaScript:** the JS/TS tool or idea I already know that is similar.
**Why this way:** the main decision and its trade-off, in 1-2 sentences.
**Interview line:** one sentence I can say in an interview.
**Words to know:** new terms, each with a one-line meaning.
**Check yourself:** one quick question for me to answer.
```

For Angular steps, use the same format, but:
- replace **Like in JavaScript** with **Like in React** (e.g. useState → signal, useEffect → effect, Context → service + inject);
- add **Old way:** one line showing the pre-signals / NgModule version (interviews and older codebases still use it).

Every entry, backend or Angular, ends with **Check yourself:** (one quick check question).

Write it as if explaining to someone new to Python, Angular and AI. Add the entry before suggesting the commit for that step.

## How you must work with me
- Go ONE step at a time. Never build everything at once.
- For each step: (1) explain the concept in 3-4 simple sentences, (2) write the code for that step only, (3) give me the exact commands and say WHY I run each one, (4) WAIT for me to run them and report back, (5) update `LEARNING.md` before suggesting the commit.
- I run the commands myself unless I ask you to.
- Keep code simple, typed and commented. No LangChain or LlamaIndex: I need to understand every line.
- When something fails, explain the error simply before fixing it.
- Be direct and concise. Ask before big assumptions.
- After each working step, suggest a commit message (Conventional Commits) and let me commit.
- The same rules apply to Angular steps: one step at a time, explain in 3-4 simple sentences, code for that step only, exact commands, wait for me to run them, update `LEARNING.md`, suggest a commit.

## Stack (Python + Angular + PostgreSQL)
- **services/api**: Python 3.12, FastAPI, Pydantic, SQLAlchemy 2 + Alembic, `pgvector`, `httpx`, `google-genai` (Gemini), `pypdf`, pytest.
- **apps/web**: Angular 22 (standalone components, signals, zoneless, OnPush, SCSS) + TypeScript, Angular CLI, Vitest. I'm learning Angular: explain every new Angular concept by comparing it to React.
- **PostgreSQL 16 + pgvector** in Docker (`pgvector/pgvector` image). `docker-compose.yml` runs db + api + web.
- **FastAPI is the ONLY service that touches the database.** Angular calls FastAPI with `HttpClient` / `httpResource` under `/api`. In development, the Angular dev server forwards `/api` to FastAPI with `proxy.conf.json` (no CORS needed). In docker-compose, nginx serves the Angular build and forwards `/api` to the api service.
- TypeScript types for API responses are generated from FastAPI's OpenAPI schema (`openapi-typescript`) into one file. Never write API types by hand.
- Gemini: key in `.env` as `GEMINI_API_KEY` (never committed; ship `.env.example`). Google retires model names often: first write a script that lists the available models, then keep the chat and embedding model names in ONE config place. Embeddings with `output_dimensionality=768` → `vector(768)` + HNSW index.
- All Gemini calls go through ONE module (`llm.py`) that logs every call, rate-limits, retries, and can be swapped for a `FakeLLM` in tests.
- Email: Gmail API with OAuth (scope `gmail.send` only) from my own account. Tokens stored locally in a git-ignored file. Check the current Google docs for the setup steps before writing them.

## Angular rules
- **Modern Angular only:** standalone components, `signal()`, `computed()`, `effect()`, `linkedSignal()`, `input()`/`output()`/`model()`, `inject()`, `@if`/`@for`/`@switch`/`@defer`, `httpResource`, Signal Forms, lazy-loaded routes.
- No NgModules, `*ngIf`/`*ngFor` or constructor injection in my code. But every `LEARNING.md` entry shows the old way in one line, because interviews and older codebases still use it.
- **Feature folders** in `apps/web/src/app`:
  - `core/`: api client, interceptors, guards
  - `shared/`: reusable UI components, pipes, directives
  - `features/today`, `features/drafts`, `features/applications`, `features/cv`, `features/stats`
- **No UI component library at first:** I build the reusable components myself (modal, table, chips). Angular CDK is allowed (drag-drop for the board).
- **Learning goal:** by the end I want advanced Angular knowledge. The web part must cover, step by step: components and templates, pipes, lifecycle hooks, signals, services and DI (providers, `InjectionToken`), routing (lazy loading, route params with input binding, guards, resolvers), `HttpClient` + interceptors + global error handling, RxJS (`switchMap`, `debounceTime`, `combineLatest`, `takeUntilDestroyed`, `toSignal`), Reactive Forms and Signal Forms (custom validators, `FormArray`), content projection and `ng-template`, custom directives, CDK drag-drop, change detection (OnPush, zoneless), `@defer`, NgRx SignalStore, testing with Vitest.
- **No auth for now** (see W9). Learn guards and interceptors through real uses: a guard that blocks Draft review when no CV is uploaded; interceptors for the `/api` base URL, a loading indicator and global error handling.

## Job data sources (free, legal)
Official public APIs only. NO scraping, and NO bots that fill in application forms on LinkedIn, Indeed or company sites.
- **Arbeitnow**: `https://www.arbeitnow.com/api/job-board-api` (no key).
- **RemoteOK**: `https://remoteok.com/api` (no key; link back required).
- **Remotive**: free public feed (few calls per day; link back required).
- **Himalayas** and **Jooble** (free key): check whether their current APIs and terms allow this use before adding them.
- Check each API's current response format before writing a fetcher.
- Each source is one small fetcher class with the same interface (`fetch() -> list[RawJob]`).
- Every job stores `source` and the original `url`; the UI links back to it.

## "Remote" is not enough
I live in Albania. Keep a job only if it is worldwide / anywhere, accepts Europe, EMEA or CET-friendly time zones, or is an international contractor role. Extract this in enrichment as `location_rule` (worldwide / europe / country_restricted / unclear) and filter on it. Drop jobs that require a language I don't speak (I speak English C1, Italian B2).

## Two ways to apply
- **Email jobs**: the posting gives an application email address. The app drafts the email and I click Send.
- **Form jobs**: the posting only has an "apply" link. The app drafts the cover letter, shows a "Copy" button and the link, and I submit it myself. Then I click "Mark as applied".
Extract `apply_email` only if it is written in the posting. Never guess or build an email address.

## Privacy
- My real CV (PDF + text) and Gmail tokens are never committed: `data/private/` is in `.gitignore`. The repo ships a FAKE sample CV in `data/samples/`.
- Personal use only: no other users, no auth, runs on my machine.

## Database (Alembic; FastAPI owns it)
- `jobs`: id, source, source_id, url, title, company, location, description, posted_at, fetched_at, content_hash (unique), search_tsv
- `job_enrichment`: job_id, skills text[], must_have text[], nice_to_have text[], seniority, years_required, languages_required, location_rule, apply_email, salary_text, enriched_at, model
- `job_embeddings`: job_id, embedding vector(768) + HNSW
- `cvs`: id, label (e.g. "frontend", "full-stack", "ai"), file_path, raw_text, profile JSONB, embedding vector(768), is_default
- `matches`: id, job_id (unique), cv_id, stage1_rank, score, matched_skills text[], missing_skills text[], why_text, evidence_quotes JSONB, grounded bool, created_at
- `drafts`: id, match_id, subject, body, cover_letter, status (draft / approved / sent / skipped), edited_by_me bool, created_at, approved_at
- `applications`: id, job_id (UNIQUE: one application per job), draft_id, method (email / form), to_email, gmail_message_id, sent_at, status (sent / replied / interview / offer / rejected / no_response), follow_up_due, notes
- `events`: id, application_id, type, detail, created_at (the history of each application)
- `llm_calls`: id, step, model, input_tokens, output_tokens, latency_ms, ok, error, created_at
- `ingest_runs`: id, source, started_at, finished_at, fetched, inserted, duplicates, ok, error

## The pipeline
**A. Ingest** (`python -m app.ingest`): fetch → normalise to `RawJob` → dedupe by `content_hash` (`ON CONFLICT DO NOTHING`) → log `ingest_runs`.

**B. Enrich** (only jobs not yet enriched): LLM structured output → `JobProfile` (skills, must/nice, seniority, years, languages, `location_rule`, `apply_email`). Only what the posting says; null if not stated. Normalise skill names in code with an alias map. Embed and store.

**C. CV**: pypdf → text → `CVProfile` (structured output), shown in the UI as editable skill chips. I can keep several CV versions with labels.

**D. Match (two stages)**
1. Cheap, no LLM: filters (`location_rule`, language, posted within N days) + vector search + full-text search → merge with Reciprocal Rank Fusion → top 50.
2. LLM-as-judge on the top 15: per requirement `met / partial / missing` + an `evidence_quote` copied from my CV. Temperature 0.
3. Guard-rail: a quote counts only if it exists in my CV text. Otherwise the requirement becomes "missing".
4. Final score calculated in CODE (must-have weight 2, nice-to-have 1; met 1.0, partial 0.5, missing 0).

**E. Draft** (only for matches above a score I set, e.g. 70)
1. Pick the CV version whose label fits the job best (code rule first; explain it).
2. LLM writes: email subject, a short email body (max ~120 words), and a cover letter (max ~200 words), using ONLY requirements marked met/partial with grounded evidence. Tone: professional, direct, no clichés.
3. Guard-rails in code, shown as warnings on the draft:
   - every skill and number in the draft must exist in my CV profile (no invented experience, no invented years);
   - the company name and job title must match the job record exactly;
   - no placeholders like "[Company]" left in the text;
   - length limits respected.
4. Save as `drafts.status = draft`.

**F. Approve** (the UI): a queue of drafts. For each: the job, score, matched and missing skills, the draft (editable), warnings, the CV that will be attached, and three buttons: **Send** (email jobs) or **Copy + open link** (form jobs), **Save edit**, **Skip**.

**G. Send**: `POST /drafts/{id}/send` → check status, check no existing application for this job → send via Gmail API with the CV attached → store `gmail_message_id`, create the `applications` row and an `events` row, in ONE transaction. A daily cap (e.g. 15) as a safety limit.

**H. Track**: a board of applications by status. I change the status by hand. `follow_up_due` = sent_at + 7 days; the app shows "follow up today" and can draft a short follow-up email, which I also approve and send by clicking. (Reading my inbox to detect replies is out of scope for now.)

**I. Schedule**: one command `python -m app.daily` runs ingest → enrich → match → draft. Help me schedule it on my computer once a day. It never sends anything.

## API (FastAPI)
- `POST /cvs`, `PATCH /cvs/{id}/profile`
- `GET /matches?min_score=`, `POST /matches/{id}/draft`
- `GET /drafts?status=draft`, `PATCH /drafts/{id}` (edit), `POST /drafts/{id}/approve`, `POST /drafts/{id}/send`, `POST /drafts/{id}/skip`, `POST /drafts/{id}/mark-applied` (form jobs)
- `GET /applications`, `PATCH /applications/{id}` (status, notes)
- `POST /admin/run-daily`, `GET /admin/stats` (jobs per source, ingest runs, LLM calls, tokens, estimated cost)

## Web (Angular)
- **Today**: new matches and the draft queue (the main screen).
- **Draft review**: described in F.
- **Applications**: board by status, follow-ups due.
- **CV**: upload versions, edit skill chips.
- **Stats**: sources, last runs, LLM usage and estimated cost this month.

## Tests and CI
- pytest with `FakeLLM` and a fake email sender (no API keys needed): normalisation from saved fixtures, dedupe, skill aliases, RRF, scoring, grounding, draft guard-rails, and the send rules (refuses unapproved drafts, refuses a second send for the same job, respects dry-run and the daily cap).
- Angular tests (Vitest): services with `HttpTestingController`, the CV guard, and the Draft review page (one draft id per send, no "send all").
- GitHub Actions on push/PR: ruff + pytest (Postgres+pgvector service) + `ng lint` (angular-eslint) + `ng test` (Vitest) + `ng build`, run in `apps/web`.

## Order of steps
**Backend**
0. ✅ Done: Repo skeleton, docker-compose, `.gitignore`, `.env.example`, model-list script, empty `LEARNING.md`.
1. ✅ Done: FastAPI + DB + first migration.
2. ✅ Done: Fetchers + dedupe + ingest runs.
3. ✅ Done: `llm.py` + enrichment (incl. `location_rule`, `apply_email`).
4. Embeddings + pgvector + full-text search.
5. CV upload → profile.
6. Matching: stage 1 (RRF) then stage 2 (judge + grounding + score in code).
7. Drafting + draft guard-rails.
8. Frontend: see the Angular track (W0-W9) below.
9. Gmail OAuth + send (dry-run first, then live with one test email to myself).
10. Applications board + follow-ups.
11. Daily command + scheduling.
12. Tests + GitHub Actions.
13. README (problem, architecture diagram, screenshots, how to run, design decisions, cost per month, what I'd improve), a 60-second pitch, and the 5 hardest interview questions about this project.

**Angular track (W0-W9)**, runs in parallel with the backend steps. It starts now with mock data shaped like the API schemas and switches to the real API as each endpoint is built.
- **W0**: Angular setup in `apps/web`. If I've already run `ng new` there, check it. If an old Next.js scaffold exists, show me and ask before deleting. Add `proxy.conf.json` and the folder structure.
- **W1**: Components and templates: Today page with mock matches (cards, pipes, `@if`/`@for`, `input`/`output`, lifecycle hooks).
- **W2**: Signals, services, DI: a matches service, filters, computed values.
- **W3**: Router + HttpClient: every page as a lazy route, `/api/health`, interceptors, the CV guard, generated API types.
- **W4**: Forms: CV skill-chips editor and draft editor (Signal Forms + Reactive Forms, validators for the length limits).
- **W5**: RxJS: filters with debounce, autosave of draft edits.
- **W6**: Advanced components: reusable modal, chips and table with content projection and `ng-template`; a custom directive; Applications board with CDK drag-drop.
- **W7**: Performance and state: OnPush/zoneless check, `@defer`, NgRx SignalStore for the draft queue, Stats page.
- **W8**: Angular tests + CI.
- **W9** (reminder, not built yet): JWT auth. When W8 is done, remind me that JWT auth (login, token storage, auth interceptor, auth guard) is still not learned, and offer to add it.

## Don't
- Don't send any email without my click on that draft. Don't add auto-send.
- Don't scrape websites or automate application forms.
- Don't invent email addresses, experience, skills or numbers.
- Don't let the LLM compute scores.
- Don't call the LLM for jobs already enriched, or for all jobs at match time (top 15 only).
- Don't commit secrets, tokens or my real CV.
- Don't move on until I confirm the current step works.
- Keep explanations short and simple; I'll ask for more.
