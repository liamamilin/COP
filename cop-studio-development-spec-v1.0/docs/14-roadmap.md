# 14 — Development Roadmap

## Phase 0 — Repository and runnable skeleton

Deliver:

- monorepo,
- frontend shell,
- FastAPI shell,
- database connection,
- migrations,
- worker process,
- Docker Compose,
- CI,
- `.env.example`,
- health endpoint.

Acceptance:

```text
docker compose up
```

opens the application and all services are healthy.

## Phase 1 — Project + source lifecycle

Deliver:

- create/edit/archive project,
- paste text,
- upload Markdown/TXT/PDF,
- add URL,
- source processing status,
- source preview.

No AI generation required yet.

## Phase 2 — COP artifact renderer

Before Harness complexity, implement rendering using fixtures.

Deliver:

- COP schema,
- sample artifact,
- Overview,
- Goal,
- Process,
- Stage,
- Concept,
- Operation pages.

This ensures the product contract is visible early.

## Phase 3 — Provider settings + basic Harness

Deliver:

- OpenAI-compatible provider,
- connection test,
- full Harness Standard mode,
- worker execution,
- generation progress,
- schema validation,
- candidate artifact.

Use one strong model for all steps.

## Phase 4 — Drafting and versioning

Deliver:

- create draft from generated candidate,
- inline edit,
- publish,
- version history,
- compare summary.

## Phase 5 — Learn Mode

Deliver:

- select Goal,
- stage-by-stage learning,
- progress,
- practice,
- checkpoint,
- completion state.

## Phase 6 — Partial refinement

Deliver:

- refine Goal,
- refine Process,
- refine Stage,
- before/after preview,
- accept/reject candidate patch.

## Phase 7 — Export and polish

Deliver:

- JSON,
- Markdown,
- Markdown bundle,
- keyboard navigation,
- error polish,
- backup docs,
- golden benchmark.

## Post-V1

Possible:

- GitHub repository adapter,
- semantic search,
- COP merge,
- compare two COPs,
- collaborative workspaces,
- cloud sync,
- public read-only share,
- adaptive learning,
- automatic quiz generation,
- spaced review,
- mobile-native client,
- richer process visualization.

## Scope control rule

Do not move a post-V1 feature into V1 unless it is necessary for:

```text
Produce COP
→ Manage COP
→ Learn COP
```

That is the V1 product.


> **V1.0 note:** `23-coding-agent-milestones.md` is the authoritative milestone execution sequence.
