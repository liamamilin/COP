# 03 — Product Requirements

## 1. V1 product scope

V1 is a complete local-first web application that supports the full COP lifecycle:

```text
Create
→ Generate
→ Review
→ Refine
→ Learn
→ Export
```

## 2. Core user flows

### Flow A — Create from a topic

1. User clicks **New COP**.
2. User enters:
   - topic,
   - optional scope,
   - current knowledge level,
   - target outcome,
   - preferred language.
3. User chooses generation depth:
   - Fast,
   - Standard,
   - Deep.
4. User runs generation.
5. Harness produces a COP draft.
6. User reviews and publishes the version.

### Flow B — Create from sources

Supported V1 inputs:

- pasted text,
- Markdown,
- TXT,
- PDF,
- URL,
- optional GitHub repository URL if public clone succeeds.

V1 must not require all source types to be implemented before the first usable release. Implement text/Markdown/PDF/URL first.

### Flow C — Refine COP

The user can:

- regenerate a Goal,
- regenerate a Main Process,
- rewrite a Stage,
- ask the harness to simplify or deepen a section,
- manually edit any text field,
- create a new version,
- compare versions.

### Flow D — Learn

1. User selects a Goal.
2. User sees Main Process overview.
3. User enters Stage 1.
4. Stage shows:
   - local outcome,
   - concepts,
   - operations,
   - explanation,
   - example,
   - implementation detail on demand.
5. User marks Stage complete.
6. User completes minimal practice.
7. User answers checkpoint questions.
8. Progress is saved.

### Flow E — Export

Export formats:

- Markdown bundle,
- single Markdown document,
- JSON,
- printable HTML.

PDF export is optional after V1.

## 3. Core screens

- Home / project list
- New project wizard
- Project workspace
- Generation run screen
- COP overview
- Goal detail
- Main Process detail
- Stage detail
- Concept / Operation explorer
- Learn Mode
- Source manager
- Version history
- Settings
- Export dialog

## 4. Project workspace layout

Recommended desktop layout:

```text
┌─────────────────────────────────────────────────────┐
│ Project Header / Version / Generate / Learn / Export│
├───────────────┬─────────────────────────────────────┤
│ Navigation    │ Main Content                        │
│               │                                     │
│ Overview      │ selected artifact section           │
│ Goals         │                                     │
│ Processes     │                                     │
│ Concepts      │                                     │
│ Sources       │                                     │
│ Versions      │                                     │
└───────────────┴─────────────────────────────────────┘
```

Do not default to a large node graph.

## 5. Functional requirements

### Project management

- create project,
- rename project,
- archive/delete project,
- duplicate project,
- list recently updated projects.

### Source management

- add/remove source,
- display source type and processing status,
- show extracted text preview,
- retry failed extraction,
- attach/detach source from generation run.

### COP generation

- generate from topic only,
- generate from selected sources,
- persist generation run,
- expose progress steps,
- allow cancellation,
- save draft artifact,
- run critic/refinement pass,
- publish as new version.

### Editing

- manual inline editing,
- regenerate selected section,
- save draft,
- undo unsaved field edits,
- create explicit version checkpoints.

### Learning

- select Goal,
- track completed Stages,
- show minimal practice,
- show checkpoint prompts,
- show “where this fits” explanation,
- mark Goal complete,
- reset progress.

### Search

V1 search:

- project titles,
- Goal titles,
- Main Process titles,
- Concept names.

Full semantic search is post-V1.

## 6. Versioning

Every published COP is immutable.

Edits create a draft derived from a version.

Publishing creates:

```text
Version N + 1
```

Store:

- created timestamp,
- parent version,
- generation run ID if applicable,
- author mode: user / harness / mixed,
- change summary.

## 7. Regeneration semantics

Never silently overwrite user-authored content.

When regenerating:

- create candidate content,
- show preview/diff,
- user accepts or rejects,
- accepted changes enter current draft.

For V1, a simple field-level before/after preview is enough.

## 8. Error experience

Errors must be actionable.

Bad:

> Generation failed.

Good:

> Source extraction succeeded, but the model response did not match the COP schema. Retry the structure pass or switch to a different model.

## 9. Empty states

Every empty screen should explain the next meaningful action.

Example project empty state:

> No COP yet. Add a topic or source, then run the Harness to generate the first draft.

## 10. Accessibility

- keyboard navigable,
- semantic headings,
- visible focus,
- sufficient contrast,
- no information encoded only by color,
- collapsible sections usable by screen reader,
- reduced-motion preference respected.

## 11. Performance targets

Reasonable V1 targets:

- initial app shell < 2.5 s on local network,
- project page interactive < 1.5 s after data received,
- section navigation instantaneous after artifact loaded,
- generation progress event latency < 2 s,
- large COP artifact with ~200 sections remains usable without full-page lag.

## 12. V1 non-requirements

Do not block V1 on:

- collaborative multi-user editing,
- public sharing,
- mobile-native app,
- social features,
- enterprise RBAC,
- vector search,
- automatic spaced repetition,
- marketplace,
- browser extension,
- real-time multi-user presence.
