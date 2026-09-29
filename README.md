# COP Studio

COP Studio is a local-first workspace that turns a topic or source set into a
Goal → Main Process → Stage → Concept × Operation learning artifact.

## Architecture

- `apps/web`: Next.js reading and learning workspace
- `backend`: FastAPI API, PostgreSQL persistence, and a separate worker
- `schemas`: canonical COP JSON Schema
- `fixtures`: validated reference COP used for seed data and tests

Published COP versions are immutable JSONB documents. Long-running generation
work is claimed by a database-backed worker; no Redis service is required.

## Implemented milestones

- M0: runnable monorepo, FastAPI, PostgreSQL migration, worker heartbeat, CI, Docker Compose
- M1: canonical schema validation, seeded LangChain reference COP, typed process-first renderer
- M2: project CRUD plus persisted text, TXT, Markdown, PDF, and public URL sources
- M3: encrypted provider settings, deterministic Mock Provider, OpenAI-compatible adapter, connection test
- M4: persisted Harness (H00–H130), database-backed run queue, SSE progress, cancellation, and crash recovery
- M5: candidate-to-draft, manual field editing, explicit publish, immutable versions, version history
- M6: partial AI refinement, before/after preview, accept/reject, user edits protected
- M7: Learn Mode, per-version progress, the full Main Process always on screen
- M8: JSON/Markdown exports, backup/restore, generated types, appearance and keyboard
  accessibility, reliable Learn navigation, lean Docker build contexts, final error states,
  and large-artifact performance gates

### The persisted Harness

Generation is a 14-step pipeline, split so that judgment and bookkeeping stay
apart:

```text
H00 intake → H10 scope → H20 research brief → H30 goals
→ H40 main processes → H50 stage enrichment
→ H60 canonicalize concepts/operations → H70 branches + shared foundation
→ H80 learning layer → H90 assemble → H100 critic → H110 refine
→ H120 validate/repair → H130 finalize
```

The model handles semantic work; code handles everything structural. In
particular, Shared Foundation detection is exact normalized-title comparison in
code rather than a model judgment, because a confident wrong answer there would
silently drop a Stage from the main line.

OpenAI-compatible structured calls include the concrete step JSON Schema in the
system prompt and validate the returned object before a checkpoint is accepted.
Fast mode is enforced in code (at most 4 Goals and 5 Stages per process), not
left as a suggestion to the model. Large cross-stage prompts use compact views
so retries cannot multiply a runaway request.

A run is a row in `generation_runs`. The worker claims one with
`FOR UPDATE SKIP LOCKED`, checkpoints after every step, and heartbeats while it
works. Consequences worth knowing:

- **A crashed worker does not strand a run.** A `running` row whose heartbeat
  went cold is requeued and resumes from its last checkpoint.
- **A failed run keeps its work.** Checkpoints survive every failure, including
  validation that could not be repaired (`needs_attention`).
- **Nothing publishes automatically.** A run produces a candidate for review;
  publishing is an explicit user action.
- **A run survives an API restart**, because no state lives in a process.

Endpoints:

```text
POST /api/v1/projects/{project_id}/generation-runs
GET  /api/v1/projects/{project_id}/generation-runs
GET  /api/v1/generation-runs/{run_id}
GET  /api/v1/generation-runs/{run_id}/progress
GET  /api/v1/generation-runs/{run_id}/events      (SSE, honours Last-Event-ID)
GET  /api/v1/generation-runs/{run_id}/candidate
POST /api/v1/generation-runs/{run_id}/cancel
```

## Drafts and versions

A finished run's candidate becomes the project's **draft**, which is the only
mutable artifact. Editing is deliberately narrow: only text fields
(`title`, `outcome`, `definition`, …) are editable, and every write re-validates
the whole artifact before it is stored.

```text
POST   /api/v1/projects/{project_id}/drafts/from-run/{run_id}
POST   /api/v1/projects/{project_id}/drafts/from-version/{version_id}
GET    /api/v1/projects/{project_id}/draft
PATCH  /api/v1/drafts/{draft_id}/metadata
PATCH  /api/v1/drafts/{draft_id}/{kind}/{entity_id}   # goals|processes|stages|concepts|operations
POST   /api/v1/drafts/{draft_id}/publish
DELETE /api/v1/drafts/{draft_id}
```

Two deliberate boundaries:

- **Reference fields are not hand-editable.** `stage_refs`, `concept_refs`, and
  `id` are structure, and structure is the code's job — the same split as Shared
  Foundation detection in H70. A PATCH that could rewrite `stage_refs` would let
  a client silently drop a Stage from the main line, which is exactly the
  failure the product exists to prevent.
- **Published versions have no mutating endpoint.** There is no PATCH or DELETE
  for a `COPVersion`; revising a live version means forking it into a new draft.
  The POST export subresource only derives a portable file from immutable JSON.
  `test_drafts.py` asserts this boundary against the OpenAPI document, so the
  guarantee survives someone re-adding a write route.

A project has at most one active draft, enforced by a unique index rather than a
read-then-write check. Creating a second returns `409 DRAFT_ALREADY_EXISTS`
instead of discarding edits the user has not published.

## Partial AI refinement

A run that names a `target` refines one Goal, Main Process, or Stage instead of
regenerating the COP. It produces a patch, not a candidate artifact, and
producing one changes nothing.

```text
GET  /api/v1/generation-runs/{run_id}/candidate-patch    # before/after preview
POST /api/v1/generation-runs/{run_id}/candidate-patch/accept
POST /api/v1/generation-runs/{run_id}/candidate-patch/reject
```

Every field the user edits by hand is recorded on the draft as a locked path, and
a proposal that touches one is refused. The refusal is reported with a reason
rather than dropped silently, so a user can see that the model tried. Accepting
re-checks the locks and refuses a patch whose "before" no longer matches the
draft, rather than discarding whatever was typed while the preview sat open.

Only `accept` writes, and only ever to the draft. There is no path from the patch
router to a `COPVersion`.

## Learn Mode

```text
GET /api/v1/projects/{project_id}/learning-progress?version_id=...
PUT /api/v1/projects/{project_id}/learning-progress
```

Progress belongs to a **version**, not a project. Publishing v2 gives you a
separate, intact history rather than overwriting the one you worked through —
which matters because v2 reuses the same entity ids, so a project-keyed row
would silently carry your v1 progress into v2.

Goal completion is derived from its Stage rows, never stored, so it cannot drift
out of agreement with the Stages it was derived from. A completed Stage can be
reopened, which is how someone revisits what they have already worked through.

The Main Process is rendered in full alongside the current Stage. That is the
product's central claim: you can always see where you are on the main line, not
just the step you are standing on.

## Export and operational hardening

Each immutable version can be exported from Version history as the canonical
JSON artifact, one readable Markdown file, or a standalone Markdown ZIP bundle.
The API endpoint is:

```text
POST /api/v1/versions/{version_id}/exports
format = json | markdown | markdown_bundle
```

Export filenames include the published version number. The generated
`packages/cop-types/generated/index.ts` is derived from the canonical JSON
Schema with `make generate-types`; CI regenerates it and rejects stale output.

Theme and density preferences are applied to the whole app, main flows expose
visible keyboard focus, and Learn Mode supports native keyboard Stage
navigation. Performance gates cover 200 Stages, multi-megabyte source text,
1,000 generation events, and 100 published versions.

## Quick start

```bash
cp .env.example .env
docker compose up --build
```

Open <http://localhost:3000>. API health is available at
<http://localhost:8000/health>.

The browser talks to the same-origin `/api/v1` path. Next proxies that path to
the internal `api:8000` service, so browser writes do not depend on the host
API port or CORS configuration. If port 3000 is occupied, choose another web
port explicitly, for example `WEB_HOST_PORT=3001 docker compose up --build`.

If port 5432 is already taken by a local PostgreSQL, the container will fail to
bind. Move it aside:

```bash
POSTGRES_HOST_PORT=55432 docker compose up --build
```

Seed the reference project after the services are running:

```bash
docker compose exec api python -m app.scripts.seed
```

## Direct development

Requirements: Node 22+, pnpm 11+, Python 3.12+, uv, and PostgreSQL 16+.

```bash
pnpm install
cd backend && uv sync --all-groups
```

Run the API, worker, and web app in separate terminals:

```bash
cd backend && uv run alembic upgrade head && uv run uvicorn app.main:app --reload
cd backend && uv run python -m app.jobs.worker
pnpm dev
```

## Environment variables

See `.env.example`. The mock provider is the default and requires no API key.
For a real endpoint set `OPENAI_COMPATIBLE_BASE_URL`,
`OPENAI_COMPATIBLE_API_KEY`, and `OPENAI_COMPATIBLE_MODEL`.
The Settings screen can also store the provider key encrypted with `APP_SECRET`;
the API returns only a masked hint.

Optional web enrichment uses Exa. Set `EXA_API_KEY` and explicitly select
"Enrich with Exa web research" for a generation run; ordinary runs never search
the web implicitly. Search results become bounded, checkpointed source excerpts,
so crash recovery does not pay for the same query twice.

## Tests and lint

```bash
make test     # provisions a throwaway PostgreSQL, runs backend + web tests
make lint
```

Browser tests are separate, because they need the real stack running:

```bash
make up           # or: POSTGRES_HOST_PORT=55432 make up
make test-e2e     # drives the draft lifecycle in Chromium
```

`make test-e2e` talks to the running development stack, so it creates its own
throwaway projects rather than touching yours. It runs serially against one
database and expects a Worker to be running, since the fixture produces a real
candidate instead of a hand-written artifact.

The backend suite needs a real PostgreSQL, because job claiming, stale-run
recovery, and the unique `(run_id, sequence)` constraint are PostgreSQL
behaviour. `make test` therefore creates a separate `cop_test` database on its
own port and never touches your development data. The suite fails rather than
skipping if no test database is reachable, so a green run always means the queue
was actually exercised.

To run the backend tests against an existing database:

```bash
TEST_DATABASE_URL=postgresql+psycopg://user:pass@localhost:5432/cop_test \
  uv run pytest            # from backend/
```

Never point `TEST_DATABASE_URL` at a database you care about: the tests
truncate every table between cases.

## Mock provider

Set `COP_PROVIDER_MODE=mock`. It is deterministic and keeps ordinary test runs
independent of paid model APIs. The mock synthesizes a real, referentially
consistent COP rather than a placeholder, so the full generation path is
exercised in mock mode. Switch scenario from Settings to test failure paths:

| Scenario | Behaviour |
| --- | --- |
| `success` | Valid COP (default) |
| `invalid` | Malformed structured output |
| `timeout` | Provider timeout |
| `rate_limit` | Rate limited, retried, then fails with `PROVIDER_RATE_LIMITED` |
| `slow` | Slow but successful |

## Backups

`make backup` briefly stops API/worker writers and creates a consistent
PostgreSQL dump plus an archive of the persistent `/data` volume under
`backups/`:

```bash
make backup
make restore BACKUP=backups/cop-studio-YYYYMMDD-HHMMSS
```

Restore replaces the current database and data volume with the selected
snapshot, then restarts and migrates the services. Keep the backup directory
until the restored app has been verified.
