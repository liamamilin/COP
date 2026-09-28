# 07 — Backend Design

## 1. Backend responsibilities

FastAPI backend owns:

- project lifecycle,
- source lifecycle,
- COP versions,
- drafts,
- generation jobs,
- provider configuration,
- artifact validation,
- learning progress,
- exports,
- event streaming.

## 2. Suggested package structure

```text
backend/
├─ app/
│  ├─ main.py
│  ├─ api/
│  │  ├─ projects.py
│  │  ├─ sources.py
│  │  ├─ generations.py
│  │  ├─ artifacts.py
│  │  ├─ learning.py
│  │  ├─ settings.py
│  │  └─ exports.py
│  ├─ core/
│  │  ├─ config.py
│  │  ├─ logging.py
│  │  ├─ security.py
│  │  └─ errors.py
│  ├─ db/
│  │  ├─ models.py
│  │  ├─ session.py
│  │  └─ migrations/
│  ├─ domain/
│  │  ├─ cop_models.py
│  │  ├─ validation.py
│  │  └─ versioning.py
│  ├─ harness/
│  │  ├─ runner.py
│  │  ├─ context.py
│  │  ├─ steps/
│  │  ├─ prompts/
│  │  ├─ providers/
│  │  └─ repair.py
│  ├─ sources/
│  │  ├─ base.py
│  │  ├─ text.py
│  │  ├─ markdown.py
│  │  ├─ pdf.py
│  │  └─ url.py
│  ├─ storage/
│  │  ├─ base.py
│  │  └─ local.py
│  ├─ jobs/
│  │  ├─ runner.py
│  │  ├─ worker.py
│  │  └─ events.py
│  └─ services/
│     ├─ project_service.py
│     ├─ artifact_service.py
│     └─ export_service.py
├─ tests/
├─ alembic.ini
└─ pyproject.toml
```

## 3. Configuration

Use environment variables plus app settings.

Required environment config:

```env
DATABASE_URL=
DATA_DIR=
APP_SECRET=
LOG_LEVEL=
```

Provider API keys should be stored through the Settings UI and encrypted before persistence.

## 4. Pydantic domain models

Create explicit models:

- `COPArtifact`
- `DomainInfo`
- `Goal`
- `MainProcess`
- `Stage`
- `Concept`
- `Operation`
- `Branch`
- `SharedFoundation`
- `Practice`
- `MentalModel`

Use model validators for referential integrity after parse.

## 5. Artifact service

Responsibilities:

- load version,
- create draft,
- patch draft,
- validate draft,
- publish version,
- compare versions,
- export version.

## 6. Patch model

Do not require JSON Patch in V1.

Use explicit domain patch endpoints.

Examples:

```text
PATCH /draft/stages/{stage_id}
PATCH /draft/goals/{goal_id}
PATCH /draft/concepts/{concept_id}
```

Each accepts partial field updates.

## 7. Regeneration service

Regeneration creates a candidate patch.

Flow:

```text
current draft/version
+
selected entity
+
user instruction
↓
harness partial regeneration
↓
candidate patch
↓
preview
↓
accept/reject
```

## 8. Worker claiming

For DB-backed queue:

1. worker polls queued jobs,
2. opens transaction,
3. selects oldest queued job,
4. marks running and assigns worker ID,
5. commits,
6. executes,
7. heartbeat updates,
8. stale running jobs can be recovered.

Use database-specific locking when available.

V1 uses PostgreSQL in development and deployment so job-claiming and migration behavior stay identical across environments.

## 9. SSE endpoint

Example:

```text
GET /api/generation-runs/{run_id}/events
```

Behavior:

- stream historical missed events first using `Last-Event-ID`,
- then poll for new events,
- send heartbeat comments,
- close when terminal state reached.

## 10. Source extraction

Extraction should be deterministic where possible.

### PDF

Use a reliable parser library first.

If extraction quality is poor:

- mark warning,
- allow user to inspect extracted text,
- do not silently hallucinate missing content.

### URL

Fetch server-side.

Store:

- final URL,
- title,
- fetched timestamp,
- text extraction result.

Respect reasonable timeouts and size limits.

## 11. Export service

Markdown export layout:

```text
README.md
overview.md
goals/
processes/
concepts/
operations/
practices/
sources.md
cop.json
```

Single-file export combines in learning-friendly order.

## 12. Error model

API errors:

```json
{
  "error": {
    "code": "COP_SCHEMA_INVALID",
    "message": "The generated artifact contains broken references.",
    "details": {}
  }
}
```

Codes should be stable.

## 13. Idempotency

Generation run creation should support an optional idempotency key.

Source processing should use content hash to avoid repeated extraction where practical.

## 14. API version

Prefix V1:

```text
/api/v1
```

## 15. Backend completion criteria

Backend V1 is complete when:

- migrations run cleanly,
- source upload works,
- a generation job survives API restart,
- worker produces a validated artifact,
- version can be published,
- draft can be edited,
- Learn Mode progress can be saved,
- export succeeds,
- integration tests pass.
