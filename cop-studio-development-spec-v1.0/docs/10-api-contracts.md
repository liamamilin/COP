# 10 — API Contracts

Base:

```text
/api/v1
```

## 1. Projects

### Create

```http
POST /projects
```

```json
{
  "title": "LangChain Agent Development",
  "domain": "LangChain Agent Development",
  "scope": "Build and understand common agent patterns",
  "preferred_language": "zh-CN"
}
```

### List

```http
GET /projects
```

### Get

```http
GET /projects/{project_id}
```

### Update

```http
PATCH /projects/{project_id}
```

### Delete

```http
DELETE /projects/{project_id}
```

Soft delete/archive is preferred.

## 2. Sources

```http
POST /projects/{project_id}/sources/upload
POST /projects/{project_id}/sources/url
POST /projects/{project_id}/sources/text
GET  /projects/{project_id}/sources
GET  /sources/{source_id}
DELETE /sources/{source_id}
POST /sources/{source_id}/reprocess
```

## 3. Generation

### Start full generation

```http
POST /projects/{project_id}/generation-runs
```

```json
{
  "mode": "standard",
  "source_ids": [],
  "settings_override": {},
  "base_version_id": null
}
```

Returns:

```json
{
  "run_id": "...",
  "status": "queued"
}
```

### Start partial regeneration

```http
POST /projects/{project_id}/generation-runs
```

```json
{
  "mode": "standard",
  "base_version_id": "...",
  "target": {
    "entity_type": "stage",
    "entity_id": "stage.tool_agent.define_tools"
  },
  "instruction": "Make this stage easier for a beginner."
}
```

### Run status

```http
GET /generation-runs/{run_id}
```

### Events

```http
GET /generation-runs/{run_id}/events
```

SSE.

### Cancel

```http
POST /generation-runs/{run_id}/cancel
```

## 4. Artifact versions

```http
GET  /projects/{project_id}/versions
GET  /versions/{version_id}
POST /projects/{project_id}/drafts/from-version/{version_id}
POST /drafts/{draft_id}/publish
```

## 5. Draft editing

```http
GET   /projects/{project_id}/draft
PATCH /drafts/{draft_id}/metadata
PATCH /drafts/{draft_id}/goals/{goal_id}
PATCH /drafts/{draft_id}/processes/{process_id}
PATCH /drafts/{draft_id}/stages/{stage_id}
PATCH /drafts/{draft_id}/concepts/{concept_id}
PATCH /drafts/{draft_id}/operations/{operation_id}
DELETE /drafts/{draft_id}
```

Every write returns validated draft summary.

## 6. Candidate regeneration patches

```http
GET  /generation-runs/{run_id}/candidate-patch
POST /generation-runs/{run_id}/candidate-patch/accept
POST /generation-runs/{run_id}/candidate-patch/reject
```

## 7. Learning

```http
GET /projects/{project_id}/learning-progress
PUT /projects/{project_id}/learning-progress
```

Example:

```json
{
  "version_id": "...",
  "goal_id": "goal.tool_agent",
  "stage_id": "stage.tool_agent.define_tools",
  "status": "completed"
}
```

## 8. Settings

```http
GET /settings
PATCH /settings
POST /settings/provider/test
```

Project:

```http
GET /projects/{project_id}/settings
PATCH /projects/{project_id}/settings
```

## 9. Export

```http
POST /versions/{version_id}/exports
```

```json
{
  "format": "markdown_bundle"
}
```

Then:

```http
GET /exports/{export_id}
```

## 10. Health

```http
GET /health
GET /ready
```

`/ready` checks database and minimum runtime requirements.

## 11. Pagination

List endpoints use:

```text
limit
cursor
```

Prefer cursor pagination.

## 12. Error codes

Suggested:

```text
PROJECT_NOT_FOUND
SOURCE_NOT_FOUND
SOURCE_EXTRACTION_FAILED
GENERATION_RUN_NOT_FOUND
GENERATION_CANCELLED
PROVIDER_NOT_CONFIGURED
PROVIDER_AUTH_FAILED
PROVIDER_RATE_LIMITED
COP_SCHEMA_INVALID
COP_REFERENCE_INVALID
DRAFT_CONFLICT
EXPORT_FAILED
VALIDATION_ERROR
```
