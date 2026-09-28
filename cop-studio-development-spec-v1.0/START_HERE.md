# COP Studio — Development Specification v1.0

Working title: **COP Studio**

COP Studio is a local-first AI knowledge-production and learning application built around the COP (Concept–Operation Process) paradigm.

Its job is not to become another notes app or generic knowledge graph. Its core product loop is:

```text
Raw knowledge / topic / sources
        ↓
COP Harness
        ↓
High-value COP Artifact
        ↓
Guided learning
        ↓
Mental model
        ↓
Independent expansion
```

## Read this first

The implementation order for a coding agent is:

1. `docs/01-product-vision.md`
2. `docs/02-cop-specification.md`
3. `docs/03-product-requirements.md`
4. `docs/04-system-architecture.md`
5. `docs/05-data-model.md`
6. `docs/06-harness-design.md`
7. `docs/07-backend.md`
8. `docs/08-frontend-ux.md`
9. `docs/09-settings.md`
10. `docs/10-api-contracts.md`
11. `docs/11-quality-evaluation.md`
12. `docs/12-testing.md`
13. `docs/13-security-deployment.md`
14. `docs/14-roadmap.md`
15. `docs/15-coding-agent-instructions.md`

Reference files:

- `schemas/cop-artifact.schema.json`
- `schemas/project-settings.schema.json`
- `prompts/harness-prompts.md`

## V1 definition

Frozen V1 must allow a user to:

1. Create a COP project.
2. Define a topic/scope or attach source material.
3. Configure generation preferences.
4. Run the COP Harness.
5. Receive a structured COP containing:
   - overview,
   - mental model,
   - goals,
   - shared foundations,
   - main processes,
   - stages,
   - concepts,
   - operations,
   - branches,
   - minimal practices,
   - expansion map.
6. Review the result in a clean visual interface.
7. Enter Learn Mode and move through a selected Main Process stage-by-stage.
8. Edit, regenerate, or refine individual COP sections.
9. Keep version history.
10. Export the COP as Markdown and JSON.

## Hard product principles

- Goal-driven, not topic-list-driven.
- Process-first, not taxonomy-first.
- Mental model before encyclopedic coverage.
- Operational sufficiency over exhaustive completeness.
- Main line must remain visible.
- Progressive disclosure: overview first, implementation details later.
- Graph is an implementation detail, not the default user interface.
- Harness output must be editable and versioned.
- The application must be useful even if generated COP coverage is incomplete.
- V1 should remain understandable to one developer and one coding agent.

## Recommended stack

- Frontend: Next.js + TypeScript + Tailwind CSS + shadcn/ui
- Backend: FastAPI + Python 3.12 + Pydantic v2 + SQLAlchemy 2
- Database: PostgreSQL 16+ for both local and hosted deployments
- Job execution: persisted database-backed worker abstraction in V1
- File storage: local filesystem in V1; S3-compatible abstraction prepared
- AI providers: provider adapter layer with OpenAI-compatible API first
- Testing: pytest + Vitest + Playwright
- Packaging: Docker Compose plus direct local-development commands

The product should remain provider-agnostic and should not couple the core domain model to any one LLM vendor.


## v1.0 freeze

This package is the implementation baseline.

Do not change the COP core model during ordinary development unless a real implementation blocker is demonstrated.

The frozen V1 path is:

```text
Create Project
→ Add Sources / Topic
→ Run COP Harness
→ Review Candidate
→ Edit Draft
→ Publish Version
→ Learn a Goal
→ Export
```

Anything not necessary for that path is secondary.

## Final engineering references


16. `docs/16-state-machines.md`
17. `docs/17-ui-component-map.md`
18. `docs/18-implementation-acceptance.md`
19. `docs/19-v1-scope-freeze.md`
20. `docs/20-harness-step-contracts.md`
21. `docs/21-ux-flows-wireframes.md`
22. `docs/22-repository-blueprint.md`
23. `docs/23-coding-agent-milestones.md`
24. `docs/24-cross-layer-consistency.md`
25. `docs/25-final-engineering-audit.md`

Reference artifact:

- `examples/reference-langchain/reference-langchain-cop.json`
