# 24 — Cross-Layer Consistency Contract

This document prevents naming drift between schema, backend, API, and frontend.

## 1. Canonical entity names

Use these exact domain names in code and documentation:

```text
Project
Source
SourceDocument
GenerationRun
GenerationEvent
COPArtifact
COPVersion
Draft
Goal
MainProcess
Stage
Concept
Operation
Branch
SharedFoundation
Practice
MentalModel
LearningProgress
```

Do not introduce synonyms such as:

```text
Flow instead of MainProcess
Step instead of Stage
Node instead of Concept
Action instead of Operation
BaseFlow instead of SharedFoundation
```

inside the domain model.

UI copy may be friendlier, but code stays canonical.

## 2. Canonical JSON keys

```text
schema_version
artifact_id
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

## 3. Canonical artifact relation fields

```text
goal_ref
stage_refs
concept_refs
operation_refs
branch_refs
practice_ref
prerequisite_goal_refs
related_concept_refs
key_operation_refs
acts_on_concept_refs
parent_stage_ref
parent_process_ref
```

Use `_ref` / `_refs`, not arbitrary foreign-key naming inside artifact JSON.

## 4. API naming

REST path plural nouns:

```text
/projects
/sources
/generation-runs
/versions
/drafts
/settings
/exports
```

Artifact child edit paths:

```text
/goals
/processes
/stages
/concepts
/operations
```

API path `/processes` maps to domain `MainProcess`.

## 5. Database naming

Snake case tables:

```text
projects
project_settings
sources
source_documents
generation_runs
generation_events
cop_versions
drafts
learning_progress
app_settings
```

Artifact internals remain JSONB.

## 6. Frontend type naming

```text
COPArtifact
Goal
MainProcess
Stage
Concept
Operation
Branch
SharedFoundation
Practice
MentalModel
```

## 7. State names

Generation:

```text
queued
running
needs_attention
completed
failed
cancelled
```

Source:

```text
created
processing
ready
failed
```

Learning:

```text
not_started
in_progress
completed
```

Do not invent alternate strings in frontend code.

## 8. Settings precedence

Always:

```text
Run override
> Project setting
> App setting
> built-in default
```

The backend resolves effective settings. Frontend may preview but does not own the merge algorithm.

## 9. Version rules

- `COPVersion` is immutable.
- `Draft` is mutable.
- `GenerationRun` produces a candidate artifact/patch.
- Accepting a candidate changes Draft.
- Publishing Draft creates COPVersion.
- LearningProgress points to a COPVersion.

## 10. CI consistency checks

CI should verify:

- schema required keys,
- sample/reference artifact validity,
- generated TS types current,
- Pydantic export compatible,
- state enums match shared definitions,
- no unresolved artifact refs in fixtures.
