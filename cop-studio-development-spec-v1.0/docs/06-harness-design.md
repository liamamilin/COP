# 06 — COP Harness Design

## 1. Purpose

The Harness automates the COP Construction Method.

It must not be treated as “one giant prompt.”

It is a controlled workflow that:

- gathers source context,
- proposes structure,
- checks structure,
- generates detail,
- criticizes,
- refines,
- validates schema,
- saves a versioned artifact.

## 2. Core principles

- Same strong model may perform multiple roles.
- Separate workflow stages are more important than fictional agent personas.
- Intermediate artifacts must be persisted.
- Structured outputs must be validated.
- Failures must be recoverable from the last successful step.
- The Harness should prefer useful incompleteness over bloated completeness.
- Sources support structure; they do not dictate final organization.

## 3. Harness pipeline

```text
Input
↓
0. Intake
↓
1. Scope Resolution
↓
2. Source Understanding
↓
3. Goal Extraction
↓
4. Main Process Construction
↓
5. Stage Decomposition
↓
6. Concept–Operation Extraction
↓
7. Branch + Shared Foundation Compression
↓
8. Mental Model + Practice Generation
↓
9. Quality Critic
↓
10. Refinement
↓
11. Schema Validation
↓
12. Publish Candidate
```

## 4. Step 0 — Intake

Inputs:

- topic,
- optional scope,
- audience level,
- target outcomes,
- sources,
- language,
- depth mode.

Output:

```json
{
  "topic": "",
  "scope_hint": "",
  "audience": "",
  "desired_outcomes": [],
  "source_ids": [],
  "language": "zh-CN",
  "depth": "standard"
}
```

## 5. Step 1 — Scope Resolution

Goal:

Produce a bounded Domain statement.

Rules:

- do not let the domain become “everything about X”,
- preserve user intent,
- state exclusions where useful,
- generate 1–3 scope warnings if ambiguity matters.

Output:

```json
{
  "domain": "",
  "scope": "",
  "target_user": "",
  "non_goals": []
}
```

## 6. Step 2 — Source Understanding

Goal:

Create a concise research brief.

Do not summarize every source.

Extract:

- core purpose,
- major capabilities,
- recurring workflow patterns,
- important constraints,
- source disagreements,
- version-specific facts.

Output:

```json
{
  "domain_summary": "",
  "capability_candidates": [],
  "workflow_candidates": [],
  "important_terms": [],
  "constraints": [],
  "evidence_index": []
}
```

## 7. Step 3 — Goal Extraction

Goal:

Identify high-value, verifiable capability outcomes.

Rules:

- prefer 3–7 goals in Standard mode,
- prefer capability results over chapter topics,
- merge duplicates,
- order from foundational to advanced when dependency exists.

Critic questions:

- Can this Goal be completed?
- Is it valuable on its own?
- Would it produce a distinct Main Process?

## 8. Step 4 — Main Process Construction

For each Goal:

- identify semantic start,
- reference Shared Foundation if available later,
- propose 3–8 core Stages,
- state final outcome.

At this phase do not generate implementation details.

Output per Goal:

```json
{
  "goal_id": "",
  "process_title": "",
  "stages": [
    {"title": "", "local_outcome": ""}
  ],
  "outcome": ""
}
```

## 9. Step 5 — Stage Decomposition

For each Stage:

Generate:

- local goal,
- why it exists,
- inputs if useful,
- local outcome,
- dependencies,
- ambiguity warning if stage is too broad.

Granularity guard:

A Stage should be understandable as:

> Complete X to obtain Y.

## 10. Step 6 — Concept–Operation Extraction

For each Stage:

Extract only high-value Concepts and Operations.

### Concept promotion test

Promote a term when:

- misunderstanding it would break the mental model,
- it is reused across stages/processes,
- it acts as a stable object category.

### Operation promotion test

Promote an action when:

- it changes or connects Concepts in a meaningful way,
- it is useful across implementations,
- it is above raw API syntax.

## 11. Step 7 — Branch and Foundation Compression

### Alternative Branch detection

Different implementations of the same Stage.

### Extension Branch detection

Optional capability attached to a base result.

### Shared Foundation detection

Find repeated leading Stage sequences across Main Processes.

Replace repeated prefixes with a stable foundation reference.

## 12. Step 8 — Mental Model and Practice

Generate:

### Mental Model

A compact system explanation plus optional simple diagram representation.

### Minimal Practice

One practice per priority Main Process when feasible.

A practice should:

- exercise the main Stage sequence,
- avoid unnecessary complexity,
- have expected observable outcome.

### Expansion Map

Show what the learner should explore next.

## 13. Step 9 — Quality Critic

The critic must explicitly check:

1. Is the Goal clear?
2. Is the main line visible?
3. Are Stages coherent?
4. Did the output become an encyclopedia?
5. Did it become an API manual?
6. Is it oversimplified?
7. Are key Concepts missing?
8. Are Operations too implementation-specific?
9. Can a user actually follow it?
10. Does it support a mental model?
11. Are repeated prefixes compressed?
12. Are claims sufficiently supported by sources where needed?

Output:

```json
{
  "severity": "pass|minor|major",
  "issues": [],
  "recommended_changes": []
}
```

## 14. Step 10 — Refinement

Apply critic changes conservatively.

Rules:

- do not expand every issue into more detail,
- preserve the main line,
- fix high-severity problems first,
- keep cognitive load low.

## 15. Step 11 — Schema Validation

Use Pydantic models.

Validation must catch:

- missing IDs,
- broken references,
- duplicate IDs,
- process without Goal,
- Stage without local goal,
- references to missing Concepts/Operations,
- invalid Branch type.

If invalid:

1. run repair prompt with validation errors,
2. retry up to configured max,
3. if still invalid, mark run `needs_attention`,
4. retain partial outputs.

## 16. Step 12 — Publish Candidate

The Harness does not silently publish over an existing user-edited version.

It creates a candidate draft.

User can:

- accept,
- inspect,
- edit,
- regenerate sections,
- publish.

## 17. Execution model

Recommended orchestration style:

```python
async def run_harness(ctx):
    ctx = await intake(ctx)
    ctx = await resolve_scope(ctx)
    ctx = await understand_sources(ctx)
    ctx = await extract_goals(ctx)

    process_results = await gather(
        *[build_process(ctx, goal) for goal in ctx.goals]
    )

    ctx = merge_processes(ctx, process_results)
    ctx = await enrich_stages(ctx)
    ctx = await extract_concepts_operations(ctx)
    ctx = await compress_branches_and_foundations(ctx)
    ctx = await generate_learning_material(ctx)
    critique = await critique(ctx)
    ctx = await refine(ctx, critique)
    artifact = validate_and_repair(ctx)
    return artifact
```

Parallelize by Goal only after shared context is stable.

## 18. Persistence checkpoints

Persist after:

- scope,
- research brief,
- goals,
- processes,
- enrichment,
- critic,
- final artifact.

A retry should resume from the last checkpoint.

## 19. Generation modes

### Fast

- 2–4 Goals
- minimal source pass
- one critic pass
- minimal practices optional

### Standard

- 3–7 Goals
- normal source pass
- full critic
- practices for priority processes

### Deep

- more source analysis
- more evidence references
- expanded practices
- additional critic/refiner cycle
- still avoid exhaustive ontology building

## 20. Model routing

V1 can use one configured model for every step.

Later routing may use:

- cheaper model for extraction,
- strongest model for structure,
- cheaper model for schema repair.

Do not make routing complexity a V1 requirement.

## 21. Failure handling

Each step returns typed status:

```text
success
retryable_failure
non_retryable_failure
partial_success
```

Retry categories:

- network,
- provider rate limit,
- invalid structured output,
- transient parse error.

Do not automatically retry:

- missing API key,
- unsupported source,
- cancelled job.

## 22. Human edits

When refining an existing artifact:

- lock user-edited fields from broad regeneration unless explicitly selected,
- regenerate the smallest useful unit,
- create a candidate patch,
- show before/after.

## 23. Harness output contract

The final contract is `cop-artifact.schema.json`.

The frontend must never parse model-native output directly.
