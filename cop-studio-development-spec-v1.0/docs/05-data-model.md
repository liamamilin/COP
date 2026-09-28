# 05 — Data Model

## 1. Core decision

V1 stores the COP itself as a versioned JSON artifact.

Relational tables manage lifecycle; JSON represents knowledge structure.

## 2. Tables

### projects

```text
id UUID PK
title
description
domain
scope
preferred_language
status
created_at
updated_at
```

### project_settings

```text
project_id FK
settings_json
updated_at
```

### sources

```text
id UUID PK
project_id FK
type
title
original_uri
blob_path
status
metadata_json
created_at
updated_at
```

### source_documents

```text
id UUID PK
source_id FK
text_path or text
content_hash
char_count
metadata_json
created_at
```

For large extracted documents, storing text in a file path is acceptable in local mode.

### generation_runs

```text
id UUID PK
project_id FK
base_version_id nullable
status
requested_mode
requested_sections_json
model_config_json
started_at
completed_at
cancel_requested
error_code nullable
error_message nullable
metrics_json
```

Statuses:

```text
queued
running
needs_attention
completed
failed
cancelled
```

### generation_events

```text
id bigint PK
run_id FK
sequence
event_type
step
payload_json
created_at
```

### cop_versions

```text
id UUID PK
project_id FK
version_number int
parent_version_id nullable
run_id nullable
artifact_json
change_summary
created_by enum(user,harness,mixed)
created_at
```

Unique:

```text
(project_id, version_number)
```

### drafts

```text
id UUID PK
project_id FK
base_version_id FK
artifact_json
updated_at
```

One active draft per project is sufficient for V1.

### learning_progress

```text
id UUID PK
project_id FK
version_id FK
goal_id
stage_id nullable
status
notes nullable
updated_at
```

### app_settings

Single-user V1:

```text
id = 1
settings_json
updated_at
```

## 3. COP artifact top-level shape

```json
{
  "schema_version": "0.1",
  "artifact_id": "uuid",
  "domain": {},
  "mental_model": {},
  "goals": [],
  "shared_foundations": [],
  "main_processes": [],
  "concepts": [],
  "operations": [],
  "branches": [],
  "practices": [],
  "expansion_map": [],
  "metadata": {}
}
```

## 4. ID rules

Every reusable entity gets a stable local ID.

Examples:

```text
goal.tool_agent
process.tool_agent
stage.tool_agent.define_tools
concept.tool
operation.bind
foundation.langchain_base
```

IDs:

- lowercase,
- dot-separated,
- stable within artifact lineage,
- not derived from display title alone after creation.

## 5. Entity references

Avoid duplicating full Concepts inside every Stage.

Stage stores references:

```json
{
  "concept_refs": ["concept.tool", "concept.schema"],
  "operation_refs": ["operation.define", "operation.bind"]
}
```

## 6. Evidence references

Any generated element may contain:

```json
"evidence_refs": [
  {
    "source_id": "...",
    "segment_id": "...",
    "quote_hint": "..."
  }
]
```

Evidence is recommended but not mandatory for every sentence.

V1 should prioritize evidence on:

- factual claims,
- version-specific claims,
- technical constraints,
- API behavior.

## 7. Main Process representation

```json
{
  "id": "process.tool_agent",
  "goal_ref": "goal.tool_agent",
  "title": "Build a Tool-Calling Agent",
  "start": {
    "type": "foundation",
    "ref": "foundation.langchain_base"
  },
  "stage_refs": [
    "stage.tool_agent.define_tools",
    "stage.tool_agent.construct_agent",
    "stage.tool_agent.execute",
    "stage.tool_agent.verify"
  ],
  "outcome": "A working agent that can invoke tools.",
  "practice_ref": "practice.tool_agent.weather"
}
```

## 8. Stage representation

```json
{
  "id": "stage.tool_agent.define_tools",
  "title": "Define tools",
  "local_goal": "Create tools that the agent can call.",
  "why_it_exists": "The model needs explicit external capabilities.",
  "concept_refs": ["concept.tool", "concept.schema"],
  "operation_refs": ["operation.define", "operation.describe"],
  "branch_refs": [],
  "implementation_details": [],
  "example": {},
  "evidence_refs": []
}
```

## 9. Concept representation

```json
{
  "id": "concept.tool",
  "name": "Tool",
  "definition": "An external capability available to the agent.",
  "role": "Extends the agent beyond model-only generation.",
  "appears_in_stage_refs": [],
  "related_concept_refs": [],
  "key_operation_refs": []
}
```

## 10. Operation representation

```json
{
  "id": "operation.bind",
  "name": "Bind",
  "definition": "Associate one capability or object with another.",
  "acts_on_concept_refs": [],
  "purpose": "",
  "common_failures": []
}
```

## 11. Version compatibility

Frontend must reject unknown **major** schema versions but tolerate additional optional fields.

Use:

```text
0.1
0.2
...
1.0
```

Until 1.0, backward compatibility is best-effort.

## 12. Database migrations

Use Alembic.

Every schema change must include:

- migration,
- downgrade where practical,
- fixture update,
- test update.
