# Published workspace readability

## Goal and boundaries

Make a published plan understandable before asking the reader to execute it:
what was generated, which scope it chose, where to start, what to do, and how to
check a result. Keep English interface labels and original generated content.

No schema migration, provider call, regeneration, automatic publishing, execution
of tutorial commands, or edits to existing artifacts/progress are authorized here.
This is a presentation and future-prompt improvement, not completion of the wider
A2/A4 curriculum-production milestones in `COP_GOAL_PLAN_TASK_METHOD.md`.

## Evidence and plan

The actual published VPN plan has 7 goals and 43 steps. Every step has instructions
and at least one expected result. It chooses deployment of existing components,
not protocol/client development. The main diagnosed problem is presentation and
scope visibility, not mechanically missing fields. This audit does not establish
the technical correctness of every generated command or claim.

- [x] Pure reader projection: derive routes, first step, and presence of actions/
  checks from the existing artifact. No API, text rewriting, or inferred facts.
- [x] Overview: explain that publishing saved a plan, expose the generated approach
  and exclusions, provide a specific first action, and simplify route disclosure.
- [x] Shared step reader: purpose → instructions → expected result/checks → help.
  Keep necessary definitions and reasoning visible; use disclosures for supporting
  evidence, examples and optional paths, not to hide load-bearing knowledge.
  Identify absent instructions/checks without inventing them.
- [x] Guided navigation: selecting a step in Learn changes the current reader,
  preserves the selected version, and never marks progress. Respect foundations
  and show explicit navigation separately from completion controls.
- [x] Future generation: isolated writing guidance reused by scope/goals/process/
  enrichment/critic/refinement prompts, without new schema fields or extra calls.
- [x] Verify pure projections, rendered ordering, missing-content cases, version
  fidelity, intercepted progress interactions, live desktop/mobile views, and
  unchanged published artifact/progress. Keep generation and draft regressions.

## Module boundaries

- `apps/web/lib/learning-guide.ts`: deterministic read-only projections.
- `components/learning-overview.tsx`: artifact-in, readable overview-out; no fetch.
- `components/stage-content.tsx`: one reader shared by Learn, details and prototype.
- `components/learn-view.tsx`: existing progress persistence stays here.
- `components/workspace.css`: workspace-scoped appearance only.
- `backend/app/harness/reader_contract.py`: future content-writing guidance only.

## Acceptance

The user can discover the chosen scope before following commands, open the first
action without navigating a database-like hierarchy, keep the route visible, and
distinguish viewing, self-reported completion, examples and actual execution.
Automated tests are engineering evidence; independent learning acceptance and
real execution of the generated VPN instructions remain unverified.

## Engineering verification

- Frontend: typecheck, lint and 98 unit/rendering tests pass.
- Backend: reader-contract, teaching-context, refinement and in-memory pipeline
  regressions (72 tests) and scoped Ruff pass;
  no database or provider was used for these checks.
- Isolated browser: foundation-first selection; navigation without writes; explicit
  frozen-version foundation/stage completion; reload persistence; failed-write
  rollback; mobile content order. All progress writes intercepted by fixtures.
- Existing isolated draft publish/discard and run/resume regressions pass.
- Library lifecycle: isolated synthetic-project tests cover title confirmation,
  cancellation/Escape focus restoration, failure retention, duplicate-click
  prevention, archive and restore. No real project was deleted or archived.
- Library previews and confirmation UI: four widths × two browser color schemes;
  lifecycle controls are outside navigation links; non-GET requests are blocked.
- Actual published project: ten page types × four viewport widths (1440, 1024,
  390, 320), with non-GET requests blocked. Published artifact and progress compare
  equal before/after. Light/dark/compact appearance is checked separately.
- No full database-backed suite or paid generation was run for this change.
