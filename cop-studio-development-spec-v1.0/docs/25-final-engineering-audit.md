# 25 — Final Engineering Audit

Status: **V1 implementation-ready**

## 1. Core conceptual contract

Pass.

Frozen hierarchy:

```text
Domain
→ Goal
→ Main Process
→ Stage
→ Concept × Operation
```

Auxiliary:

```text
Zero State
Shared Foundation
Branch
Implementation Detail
Practice
Mental Model
```

No graph database or formal ontology is required.

## 2. Product loop

Pass.

```text
Create
→ Source/Topic
→ Generate
→ Review
→ Draft/Edit
→ Publish
→ Learn
→ Export
```

Each transition has a defined UI and backend state.

## 3. Persistence model

Pass after simplification.

- PostgreSQL 16+ only.
- COP artifact stored as JSONB.
- Published version immutable.
- One active Draft per project.
- GenerationRun owns Harness execution.
- LearningProgress points to published version.

## 4. Long-running work

Pass.

- separate worker,
- persisted job row,
- heartbeat,
- checkpoints,
- cancellation,
- SSE progress,
- stale-run recovery.

No Redis/Celery required.

## 5. Schema consistency

Pass with V1.0 rule:

Canonical schema includes:

```text
domain
mental_model
goals
shared_foundations
main_processes
stages
concepts
operations
branches
practices
expansion_map
metadata
```

`stages` is first-class and required.

## 6. User-edit safety

Pass.

```text
Published Version
→ Draft
→ user/AI changes
→ explicit Publish
```

AI regeneration creates candidate patch.

No silent overwrite.

## 7. Harness implementability

Pass after adding exact H00–H130 contracts.

Semantic work is separated from deterministic work.

Deterministic:

- ID/reference handling,
- assembly,
- schema validation,
- versioning,
- diff.

LLM:

- scope,
- Goal discovery,
- process design,
- Stage enrichment,
- semantic canonicalization,
- critic/refinement.

## 8. UX

Pass after wireframe specification.

Important invariant:

> User sees Goal and Main Process before detail.

Learn Mode is first-class.

Graph visualization remains optional/post-V1.

## 9. V1 scope

Pass after freeze.

Removed as V1 dependencies:

- auth/accounts,
- GitHub ingestion,
- vector search,
- cloud collaboration,
- PDF export,
- Redis,
- graph editor,
- multi-model routing.

## 10. Reference artifact

Pass.

A current LangChain COP demonstrates the intended quality and structure and can be used for:

- frontend seed,
- schema fixtures,
- Harness golden tests,
- human design reference.

## 11. Remaining implementation decisions

Coding agent may choose ordinary implementation details such as:

- exact component file names,
- exact CSS spacing,
- exact PDF parser library,
- exact encryption library,
- exact diff library.

These choices must not alter frozen domain semantics.

## 12. Freeze decision

Do not perform another broad design pass before development.

Future spec changes should be driven by:

1. an implementation blocker,
2. a failed end-to-end test,
3. a real COP generation quality failure,
4. observed UX failure.

Otherwise implement the specification.
