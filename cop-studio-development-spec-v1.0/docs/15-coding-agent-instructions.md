# 15 — Coding Agent Instructions

This document is the execution contract for the coding agent.

## 1. Objective

Build a complete, runnable V1 of COP Studio from this documentation.

Do not build only mockups or disconnected code snippets.

The repository must run end-to-end.

## 2. Priority

If documentation conflicts, use this order:

1. `02-cop-specification.md`
2. `03-product-requirements.md`
3. `04-system-architecture.md`
4. this document
5. remaining implementation documents

If a detail remains unspecified, choose the simplest reasonable implementation that preserves the product principles.

## 3. Do not overengineer

Avoid:

- microservices,
- Kubernetes,
- event buses,
- graph databases,
- complex CQRS,
- premature plugin systems,
- unnecessary abstraction layers.

Use clear modules and interfaces where future replacement is genuinely likely:

- AI provider,
- file storage,
- job runner,
- source adapter.

## 4. Required runtime quality

The final repository must include:

- working frontend,
- working backend,
- working worker,
- working database migrations,
- working mocked AI provider,
- working real OpenAI-compatible provider,
- sample COP project,
- automated tests,
- Docker Compose,
- setup instructions.

## 5. Coding standards

### Python

- Python 3.12+
- typed code
- Ruff
- pytest
- Pydantic v2
- SQLAlchemy 2
- Alembic

### TypeScript

- strict mode
- ESLint
- no `any` unless justified
- Vitest
- Playwright

## 6. Product principles that must survive implementation

- Main Process is more important than graph visualization.
- User sees Goals and Stages before deep detail.
- No silent overwriting of user edits.
- Harness is recoverable and versioned.
- API syntax is not the primary knowledge structure.
- Shared Foundations reduce repetition.
- Learn Mode is a first-class experience.
- COP remains useful when incomplete.

## 7. Implementation sequence

Implement in roadmap order.

Do not start with Harness prompt complexity before:

- schema exists,
- artifact fixture renders,
- project lifecycle works.

## 8. Seed data

Ship at least one realistic seed artifact:

```text
LangChain Agent Development
```

It can be fixture data and does not need to be generated live.

The fixture should exercise:

- multiple Goals,
- Shared Foundation,
- Main Processes,
- Stages,
- Concepts,
- Operations,
- Alternative Branch,
- Extension Branch,
- Practice.

## 9. Mock provider

Implement a deterministic mock provider so the entire application can be developed without external API access.

The mock should support:

- success,
- invalid structured output,
- timeout,
- rate limit,
- slow generation.

## 10. Live provider

Implement OpenAI-compatible endpoint support:

- base URL,
- API key,
- model,
- structured JSON request strategy,
- timeout,
- retry.

Provider-specific quirks must stay inside provider adapter.

## 11. Harness implementation rule

Each harness step:

- has typed input,
- has typed output,
- persists checkpoint,
- emits progress event,
- can fail with structured error.

Do not expose model chain-of-thought.

## 12. UI quality bar

Do not deliver a default-admin-dashboard look.

The UI should feel like a focused knowledge workspace.

Requirements:

- clear typography,
- consistent spacing,
- strong hierarchy,
- meaningful empty states,
- polished loading states,
- readable process visualization,
- no giant graph as landing view.

## 13. No fake functionality

Do not include buttons that do nothing.

If a feature is not implemented:

- hide it,
- or clearly mark it as unavailable in the current version.

## 14. Documentation

Repository root README must include:

```text
What the product is
Architecture
Quick start
Development setup
Environment variables
How to run tests
How to use mock provider
How to configure real provider
How to back up data
```

## 15. Acceptance scenario

A fresh developer should be able to:

```text
git clone
cp .env.example .env
docker compose up
open browser
create project
paste source text
use mock provider
generate COP
review artifact
publish version
enter Learn Mode
complete a Stage
export Markdown
```

without modifying source code.

## 16. Completion report

When implementation is complete, produce:

- changed files summary,
- architecture summary,
- commands to run,
- test results,
- known limitations,
- next recommended phase.

Do not claim completion if the end-to-end acceptance scenario has not been executed.


## 17. V1.0 freeze documents

Before coding, also read:

- `19-v1-scope-freeze.md`
- `20-harness-step-contracts.md`
- `21-ux-flows-wireframes.md`
- `22-repository-blueprint.md`
- `23-coding-agent-milestones.md`
- `24-cross-layer-consistency.md`
- `25-final-engineering-audit.md`
- `examples/reference-langchain/reference-langchain-cop.json`

These documents override earlier optional/ambiguous implementation suggestions where they conflict.
