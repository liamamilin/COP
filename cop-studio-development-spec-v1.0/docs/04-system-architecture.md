# 04 — System Architecture

## 1. Architecture goals

The system must be:

- simple enough for a coding agent to implement and maintain,
- modular enough to swap LLM providers,
- resilient to long-running generation jobs,
- versioned,
- local-first,
- capable of hosted deployment later,
- able to evolve without rebuilding the domain model.

## 2. High-level architecture

```text
                    ┌───────────────────────┐
                    │      Next.js UI       │
                    │ review / learn / edit │
                    └───────────┬───────────┘
                                │ HTTP/SSE
                    ┌───────────▼───────────┐
                    │       FastAPI         │
                    │ REST + orchestration  │
                    └───────┬───────┬───────┘
                            │       │
                 ┌──────────▼─┐   ┌─▼───────────────┐
                 │ PostgreSQL │   │  Worker Process  │
                 │ metadata   │   │  COP Harness     │
                 │ artifacts  │   └──────┬──────────┘
                 └────────────┘          │
                                        │
                         ┌───────────────▼──────────────┐
                         │ AI Provider Adapter Layer    │
                         │ OpenAI-compatible / others   │
                         └──────────────────────────────┘
```

## 3. Process separation

Run at least two backend processes:

### API server

Handles:

- CRUD,
- artifact reads,
- settings,
- source upload metadata,
- job creation,
- job status,
- event streaming.

### Worker

Handles:

- source extraction,
- long-running generation,
- critic/refiner passes,
- export creation.

This prevents LLM generation from blocking request handlers.

## 4. Job system

V1 should avoid a heavy distributed queue unless needed.

Use:

- `generation_runs` table,
- status field,
- worker polling/claim mechanism,
- heartbeat,
- cancellation flag,
- append-only `generation_events`.

This is sufficient for single-machine V1.

Abstract behind:

```python
class JobRunner:
    enqueue(...)
    cancel(...)
    heartbeat(...)
```

A Redis-based queue can replace it later.

## 5. Storage strategy

### Database

Store:

- projects,
- project settings,
- sources,
- extracted-source metadata,
- generation runs,
- COP versions,
- learning progress,
- app settings.

### COP artifact

Store each version as a normalized JSON document in a JSON/JSONB column.

Do **not** fully normalize every Concept and Stage into dozens of relational tables in V1.

Reasons:

- schema will evolve,
- artifact is naturally hierarchical,
- versioning is simpler,
- UI reads one coherent object,
- exports are straightforward.

Add derived searchable indexes later.

## 6. File storage

V1:

```text
data/
├─ uploads/
├─ extracted/
└─ exports/
```

Use a storage interface:

```python
class BlobStore:
    put(...)
    get(...)
    delete(...)
```

Implement `LocalBlobStore` first.

Future:

- S3,
- R2,
- MinIO.

## 7. Event streaming

Generation progress should use Server-Sent Events.

Why SSE:

- server-to-client only,
- simpler than WebSockets,
- ideal for progress/log stream,
- easy browser support.

Event examples:

```json
{"type":"run.started","step":"scope"}
{"type":"step.completed","step":"goal_extraction"}
{"type":"artifact.partial","section":"goals"}
{"type":"run.completed","version_id":"..."}
```

## 8. Provider architecture

Core code must not know provider-specific APIs.

```python
class LLMProvider:
    async def generate_structured(...)
    async def generate_text(...)
    async def health_check(...)
```

Initial adapters:

1. OpenAI-compatible
2. OpenAI native if useful
3. Anthropic optional

OpenAI-compatible support is the priority because it covers many providers.

## 9. Source extraction architecture

```text
Upload / URL
↓
Source Adapter
↓
Normalized Text
↓
Optional segmentation
↓
Source Document
```

Adapters:

- PlainTextAdapter
- MarkdownAdapter
- PDFAdapter
- URLAdapter
- GitHubAdapter (optional V1.1)

Each produces:

```json
{
  "source_id": "...",
  "title": "...",
  "text": "...",
  "metadata": {},
  "segments": []
}
```

## 10. Deployment modes

### Local mode

Primary V1.

```text
docker compose up
```

or direct:

```text
pnpm dev
uvicorn ...
python worker.py
```

### Hosted mode

Supported structurally, but not the first product target.

Hosted mode later adds:

- authentication,
- cloud object storage,
- managed database,
- secret vault,
- multi-user isolation.

## 11. Observability

V1 must log:

- request ID,
- generation run ID,
- project ID,
- harness step,
- model,
- latency,
- token usage if provided,
- retry count,
- structured-output validation errors.

Do not log API keys or raw secrets.

## 12. Architecture principle

Keep the COP artifact as the stable contract between:

```text
Harness
↔ Backend
↔ Frontend
↔ Export
↔ Learning Mode
```

Everything else can evolve around this contract.
