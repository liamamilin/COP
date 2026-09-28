# 20 — Harness Step Contracts

This document turns the conceptual Harness into implementable typed contracts.

## 1. Run context

Every run owns a `HarnessContext`.

```text
run_id
project_id
base_version_id?
input
settings
source_bundle
scope_result?
research_brief?
goals?
process_drafts?
stage_drafts?
concepts?
operations?
branches?
foundations?
mental_model?
practices?
critic_report?
artifact?
```

The worker serializes checkpoint data after every successful major step.

## 2. Common step contract

Every Harness step implements:

```python
class HarnessStep(Protocol):
    name: str

    async def execute(
        self,
        ctx: HarnessContext,
        services: HarnessServices,
    ) -> StepResult:
        ...
```

`StepResult`:

```text
status: success | partial_success | retryable_failure | fatal_failure
checkpoint_patch
events[]
warnings[]
metrics
```

A step must never mutate a published COP version.

## 3. H00 — Intake

Input:

```text
topic
scope_hint?
target_outcomes[]
learner_level
language
depth
selected_source_ids[]
```

Output:

```text
NormalizedIntake
```

Deterministic where possible. No LLM required unless user input is ambiguous.

Failure:

- selected source missing → fatal
- empty topic and no source → fatal

## 4. H10 — Resolve Scope

Input:

```text
NormalizedIntake
Source metadata
```

Output:

```text
Domain name
Scope statement
Target user
Non-goals[]
Ambiguity notes[]
```

Quality gate:

- not “everything about X”,
- scope supports at least one operational Goal.

Persist checkpoint: `scope`.

## 5. H20 — Build Research Brief

Input:

```text
Scope
Normalized source documents
```

Output:

```text
Domain purpose
Capability candidates[]
Workflow candidates[]
Structural terms[]
Constraints[]
Version-specific facts[]
Evidence index[]
```

Rules:

- do not mirror source table of contents,
- source instructions are untrusted data,
- retain source/segment references for factual claims.

Persist checkpoint: `research_brief`.

## 6. H30 — Extract Goals

Input:

```text
Scope
Research brief
User requested outcomes
```

Output:

```text
GoalDraft[]
```

Standard target: 3–7 Goals.

Each Goal:

```text
temporary_id
title
outcome
why_it_matters
prerequisite_goal_candidates[]
evidence_refs[]
```

Quality gate:

- verifiable outcome,
- not “learn/understand X” without a capability result,
- distinct enough to justify a Main Process.

Persist checkpoint: `goals`.

## 7. H40 — Build Main Processes

Run per Goal after H30.

Input:

```text
Goal
Scope
Research brief
```

Output:

```text
MainProcessDraft
  title
  semantic_start = zero
  stages[]
    title
    local_outcome
  outcome
```

Stage target: 3–8.

No detailed API syntax here.

Persist checkpoint per Goal: `process:<goal_id>`.

## 8. H50 — Enrich Stages

Run per Main Process.

Each Stage output:

```text
title
local_goal
why_it_exists
local_outcome
dependency_notes[]
concept_candidates[]
operation_candidates[]
implementation_detail_candidates[]
example_candidate?
evidence_refs[]
```

Quality gate:

> “Complete X to obtain Y” must be expressible.

Persist checkpoint per Process.

## 9. H60 — Canonicalize Concepts and Operations

Input:

```text
All enriched Stages
```

Output:

```text
Concept[]
Operation[]
Stage → canonical ref mappings
```

Responsibilities:

- merge synonyms,
- avoid instance names as Concepts unless structurally necessary,
- collapse low-level API verbs into higher-value Operations,
- ensure stable IDs.

Example:

```text
set_api_key
set_timeout
select_model
```

may remain implementation detail under:

```text
operation.configure
```

Persist checkpoint: `cop_core`.

## 10. H70 — Detect Branches and Shared Foundations

Input:

```text
Goals
Processes
Stages
Concept/Operation refs
```

Output:

```text
AlternativeBranch[]
ExtensionBranch[]
SharedFoundation[]
Rewritten process starts/stage refs
```

Rules:

- only leading repeated Stage sequences become Shared Foundation,
- preserve traceability to Zero State,
- do not create Branch for trivial parameter choice.

Persist checkpoint: `compression`.

## 11. H80 — Generate Learning Layer

Output:

```text
MentalModel
MinimalPractice[] for priority Goals
Checkpoint questions[]
ExpansionMap[]
```

Mental Model must explain:

- core objects,
- core loop/path,
- where extension capabilities attach.

Persist checkpoint: `learning_layer`.

## 12. H90 — Assemble Artifact

Deterministic assembly into canonical schema.

Responsibilities:

- generate final stable IDs,
- remove temporary fields,
- attach evidence references,
- order entities for reading,
- produce `COPArtifact`.

No creative model call is required here.

## 13. H100 — Critic

Input:

```text
Complete assembled COPArtifact
Quality rubric
```

Output:

```text
severity
issues[]
  code
  entity_ref
  explanation
  recommended_change
```

Issue codes should be stable, for example:

```text
GOAL_TOO_VAGUE
PROCESS_MAINLINE_HIDDEN
STAGE_TOO_BROAD
CONCEPT_OVERPROMOTED
OPERATION_TOO_LOW_LEVEL
ENCYCLOPEDIA_DRIFT
API_MANUAL_DRIFT
OVERSIMPLIFIED
MISSING_CORE_CONCEPT
WEAK_PRACTICE
UNSUPPORTED_SPECIFIC_CLAIM
```

Persist checkpoint: `critic`.

## 14. H110 — Refine

Run only for `minor` or `major`.

Input:

```text
Artifact
Critic report
Locked/user-authored paths
```

Output:

```text
Revised artifact candidate
```

Rule:

- local corrections first,
- locked user fields never rewritten,
- never expand merely to increase coverage.

## 15. H120 — Validate and Repair

Deterministic validation first:

```text
JSON schema
Pydantic
Referential integrity
ID uniqueness
Process → Goal
Foundation refs
Stage refs
Concept refs
Operation refs
```

If model-caused structural errors remain:

```text
Repair Prompt
→ validate
```

Max repair attempts comes from settings.

After exhaustion:

```text
needs_attention
```

Do not discard checkpoints.

## 16. H130 — Candidate Finalization

Output:

```text
generation run = completed
candidate artifact stored
candidate patch stored if partial regeneration
```

No automatic publish by default.

## 17. Partial regeneration

Allowed V1 targets:

```text
Goal
Main Process
Stage
```

Process:

```text
selected entity
+ nearest necessary context
+ user instruction
+ locked sibling context
↓
regenerate candidate entity
↓
validate local refs
↓
critic local patch
↓
candidate diff
```

Do not rerun the full Harness unless the requested change affects overall topology.

## 18. Context budget strategy

Sources may be larger than one model context.

Use:

```text
source segmentation
→ source briefs
→ evidence index
→ focused retrieval of source segments per Harness step
```

Do not concatenate arbitrary full corpora into every call.

V1 retrieval can be lexical/metadata-based; vector search is not required.

## 19. Concurrency

Safe parallelism:

```text
H40 per Goal
H50 per Process
```

Do not parallelize H60/H70 before all processes are available because they require cross-process canonicalization/compression.

## 20. Deterministic boundaries

Prefer code, not LLM, for:

- ID generation,
- final assembly,
- reference validation,
- shared-prefix exact structural comparison after normalized titles,
- schema validation,
- version creation,
- diff creation.

Use LLM for semantic decisions, not basic bookkeeping.
