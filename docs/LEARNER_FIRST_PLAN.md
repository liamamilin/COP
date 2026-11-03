# Learner-first product and content plan

## Product rule (user requirement)

This product is for people. Interaction must be comfortable; content must help a
learner understand and accomplish a real task. Restrained means reducing irrelevant
burden, not omitting the logic or prerequisites a person needs.

Engineering tests, schema validity, number of steps, clicks on Complete, or the
presence of commands are **not** evidence that someone learned the capability.

## Observed problems in the existing VPN plan

- A configuration-writing step provides a validation command, but not the complete
  configuration or a field-by-field mapping. The method is incomplete despite
  passing the existing field-presence checks.
- Some definitions enumerate terms (ACME, SNI, TLS, etc.) instead of explaining
  them in plain language. A novice needs a concrete example and the causal role.
- H50 previously received a process outline and source IDs, but not the learner
  profile, scope, prerequisite goal outputs, or source excerpts.
- Balanced density requested only two implementation details, and normalization
  silently discarded the rest. That can delete essential setup/check/recovery.
- H60's compact projection removed the action/reason context from concept writing.
- `dependency_notes` are temporary checkpoint data and do not survive assembly.
  A formal per-step input/output contract remains a separate design task; displaying
  the previous outcome is contextual help, not proof of a correct handoff.

## Instructional acceptance rubric

1. **Starting point**: explain assumed knowledge, resources, versions and permissions;
   never treat a planned prerequisite as completed work.
2. **Conceptual scaffold**: explain the necessary object in plain language, show an
   example, distinguish a confusable object, and connect it to the coming operation.
3. **Causal chain**: explain why this action changes this object and produces the
   expected result. Name the source of each input or placeholder.
4. **Worked method**: provide one complete default path using consistent files,
   values and environment. Configuration writing needs the configuration, not only
   a test command. Keep critical cautions beside the action.
5. **Practice**: start from the same task; change one meaningful condition. Fade
   support gradually rather than replacing explanation with unexplained brevity.
6. **Assessment**: check the real result and explain why the check is relevant.
   Include a failure interpretation and a nearby transfer question. Self-reported
   completion does not establish independently verified performance.

## Low-coupling implementation and status

- [x] Library: full-width layout; real, read-only published-route previews rather
  than decorative fillers; no fixed card height or viewport-sized empty container.
  Preview fetching stays in the server page; projection and CSS remain independent.
- [x] Shared reader: expose concept definition/role and step reasoning before the
  method; show previous planned output and the next step without fabricating an
  input dependency. The original published text is unchanged.
- [x] Enrichment context: one pure checkpoint projection supplies learner/scope,
  declared prerequisite outcomes, bounded source excerpts and research constraints.
  It uses the existing H50 call, with no additional model pass.
- [x] Compression policy: density now targets 2/6/10 details, not a truncation rule.
  Valid returned instructions are preserved; exceeding a target is reported.
- [x] Concept writing: retain bounded action/reason context and request explanations
  that connect objects to operations instead of an acronym list.
- [x] Library lifecycle: independent confirmation controls reuse existing API
  semantics. Delete requires typing the title; Archive is reversible. Deletion is
  separate from the navigation link and is not a physical data purge.
- [x] Full lesson contract (experimental sidecar, not COP 0.2): explicit starting
  point/resources, path boundaries, inputs/outputs with persistence, concept
  explanations and causal links, bound methods, worked case, checks, practice and
  explain/diagnose/transfer assessment. It renders from a separate reader and does
  not change published COP 0.1. See `docs/CORE_LEARNING_EXECUTION.md`.
- [x] Teaching-quality structural gate: stale content, missing/forward producers,
  ephemeral handoffs, missing file bodies, unknown concepts/operations, path gaps,
  uncovered methods, inconsistent examples and missing assessment are rejected;
  a non-code unit is also accepted. Semantic correctness is still a separate,
  unproven layer.
- [ ] Validate a complete minimal unit with a representative learner: ask them to
  do it, explain a choice, diagnose one failure, then handle one nearby variation.
  Record where they needed outside help. Do not replace this with model self-grading.
  Worksheet: `docs/LEARNING_UNIT_ACCEPTANCE.md` (status PENDING).
- [ ] Only after this acceptance, regenerate a candidate with explicit user budget/
  scope approval. Review differences and publish only by explicit user decision.
  A hand-authored sample does not establish stable automatic production.

## Safety and honest delivery

No paid generation, actual tutorial command execution, real project deletion,
automatic draft creation/publishing, or edits to existing artifact/progress are
part of this increment. Existing published lessons are **not automatically fixed**
by changing future-generation code. There has not yet been a new-model generation
or independent learning-effectiveness acceptance of these changes.

## Verification of this increment

- Typecheck/lint and 110 frontend tests pass. Teaching context, lossless detail
  normalization, reader-contract/refinement, learning-unit contract/schema and
  in-memory Mock pipeline regressions (86 tests) pass without a database or paid
  provider; scoped Ruff passes.
- Synthetic browser tests cover the complete lifecycle interaction and explicit
  versioned learning-progress interactions, including failure and duplicate clicks.
- Isolated learning-unit browser regression covers bound method content, reading
  order, graduated hints, local save/reload/export/import, path-specific work,
  fail-closed revision mismatch and mobile order, with all non-local requests
  blocked. The prototype never writes project progress or calls a provider.
- Fixture build is deterministic and the source COP artifact is byte-unchanged.
- Actual app checks block non-GET requests: homepage at four widths × two color
  schemes; ten workspace page types at four widths. Project lists, published
  artifact and learning progress compare equal before and after.
- These results establish implementation behavior, not instructional correctness
  or mastery. The complete-lesson and human-learning acceptance items above remain
  pending; no new generation was run to claim otherwise.
