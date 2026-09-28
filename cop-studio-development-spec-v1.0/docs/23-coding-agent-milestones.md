# 23 — Coding-Agent Milestones

The coding agent should complete and verify one milestone before beginning the next.

## M0 — Runnable skeleton

Build:

- monorepo,
- Next.js shell,
- FastAPI,
- worker,
- PostgreSQL,
- Alembic,
- Docker Compose,
- health endpoints,
- CI skeleton.

Acceptance:

```text
docker compose up
GET /health = 200
web page loads
migration succeeds
worker heartbeat visible
```

Do not implement Harness prompts yet.

## M1 — Canonical COP renderer

Build:

- canonical schema integration,
- generated frontend types,
- seed project,
- Reference COP rendering,
- Overview,
- Goals,
- Main Process,
- Stage,
- Concept,
- Operation.

Acceptance:

- seed Reference COP can be browsed end-to-end,
- broken reference fixture fails validation,
- no AI provider required.

Do not build source ingestion yet.

## M2 — Project + source lifecycle

Build:

- project CRUD,
- source paste/upload/URL,
- TXT/Markdown/PDF extraction,
- source preview,
- source state machine,
- file storage abstraction.

Acceptance:

- create project,
- add each V1 source type,
- restart services,
- sources remain available,
- bad source produces actionable failure.

## M3 — Settings + providers

Build:

- settings hierarchy,
- encrypted provider secret,
- OpenAI-compatible adapter,
- Mock Provider,
- connection test.

Acceptance:

- Mock Provider works without secrets,
- invalid live key returns clear error,
- API key never returned in plaintext.

## M4 — Persisted Harness

Build H00–H130.

Build:

- generation queue,
- worker claim,
- progress events,
- checkpoints,
- critic,
- repair,
- candidate artifact.

Acceptance:

```text
topic/source
→ run
→ streamed progress
→ validated candidate COP
```

Test:

- malformed response,
- timeout,
- rate limit,
- cancellation,
- API restart.

## M5 — Draft + publish + versioning

Build:

- candidate → draft,
- manual edit,
- publish,
- immutable versions,
- version list,
- discard draft.

Acceptance:

- published version cannot be changed,
- user edits survive refresh,
- v2 records parent v1.

## M6 — Partial AI refinement

Build:

- Goal refinement,
- Main Process refinement,
- Stage refinement,
- candidate patch,
- before/after preview,
- accept/reject.

Acceptance:

- rejecting changes nothing,
- accepting modifies Draft only,
- locked/user-edited sibling content is preserved.

## M7 — Learn Mode

Build:

- Goal selection,
- Stage sequence,
- progress persistence,
- implementation detail expansion,
- practice,
- checkpoints,
- Goal completion.

Acceptance:

- reload does not lose progress,
- switching artifact version does not corrupt progress records,
- full Main Process stays visible.

## M8 — Export + operational hardening

Build:

- JSON export,
- single Markdown,
- Markdown bundle,
- backup/restore,
- keyboard accessibility,
- final error states,
- large artifact performance.

Acceptance:

- frozen end-to-end acceptance path passes,
- no dead buttons,
- all tests green.

## Milestone rule

A coding agent must not call the project complete after UI rendering or Harness generation alone.

V1 complete = M0 through M8 accepted.
