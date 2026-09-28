# 08 — Frontend and UX

## 1. UX goal

The interface must preserve the COP hierarchy.

The user should always know:

- where they are,
- which Goal they are pursuing,
- which Stage they are in,
- what matters now,
- what detail is optional.

## 2. Design principle

Do not make the primary experience a giant knowledge graph.

Primary navigation is hierarchical and process-oriented.

Graph/map visualization is secondary.

## 3. Information architecture

```text
Home
└─ Project
   ├─ Overview
   ├─ Goals
   │  └─ Goal
   │     └─ Main Process
   │        └─ Stage
   ├─ Concepts
   ├─ Operations
   ├─ Sources
   ├─ Learn
   ├─ Versions
   └─ Settings
```

## 4. Project Overview

Header:

- title,
- domain,
- active version,
- generation status,
- `Generate / Refine`,
- `Learn`,
- `Export`.

Body:

### Mental Model

Simple diagram or structured flow.

### Goal Map

Cards ordered by dependency.

### Shared Foundation

Collapsed by default after first read.

### Recent activity

- last generated,
- last edited,
- learning progress.

## 5. Goal screen

Display:

- Goal statement,
- why it matters,
- prerequisite Goal(s),
- Main Process horizontal/vertical Stage strip,
- expected outcome,
- minimal practice,
- extensions.

Primary CTA:

> Start learning this process

## 6. Main Process screen

Recommended layout:

```text
Process title
Outcome

[Foundation]
   ↓
[Stage 1]
   ↓
[Stage 2]
   ↓
[Stage 3]
   ↓
Goal
```

Clicking Stage opens details.

Keep the full process visible in a sticky side/top rail when possible.

## 7. Stage screen

Stage should emphasize:

1. Local Goal
2. Why this Stage exists
3. Key Concepts
4. Key Operations
5. Minimal example
6. Branches
7. Implementation Detail
8. Evidence

Default collapsed:

- low-level API,
- long examples,
- evidence details,
- advanced notes.

## 8. Concept screen

A Concept page should answer:

```text
What is it?
Why does it exist?
Where does it appear?
What can I do with it?
What is it related to?
```

Avoid encyclopedia-length text.

## 9. Learn Mode

Learn Mode should feel different from edit/review mode.

### Header

```text
Goal
Stage X of Y
Progress
Exit Learn Mode
```

### Stage content

- local goal,
- mental-model explanation,
- concept cards,
- operation cards,
- example,
- optional “show implementation”,
- complete Stage button.

### Navigation

- Previous
- Mark complete
- Next

### End of process

Show:

- Goal achieved,
- practice,
- checkpoint questions,
- related next Goals.

## 10. Generation UX

Generation screen shows meaningful phases:

```text
Defining scope
Understanding sources
Finding high-value goals
Building main processes
Extracting concepts and operations
Compressing shared foundations
Generating learning material
Reviewing quality
Finalizing artifact
```

Do not show internal chain-of-thought or raw hidden reasoning.

Show:

- current step,
- completed steps,
- warnings,
- elapsed status,
- cancel button.

## 11. Editing UX

Manual edits:

- inline edit,
- explicit save,
- unsaved indicator.

AI refinement:

- “Refine with AI” button,
- instruction box,
- before/after preview,
- accept/reject.

Do not replace user content without preview.

## 12. Version UX

Version history shows:

```text
v3 — Sep 28 — mixed — Added RAG process
v2 — Sep 28 — harness — Initial deep generation
v1 — Sep 28 — harness — Initial draft
```

Compare view:

- added,
- removed,
- changed,
- section-level diff.

V1 does not need character-perfect rich diff.

## 13. New project wizard

Step 1 — Topic

```text
What do you want to learn or model?
```

Step 2 — Scope

Optional suggestions:

- use framework,
- build application,
- understand architecture,
- perform workflow.

Step 3 — Sources

- paste,
- upload,
- URL.

Step 4 — Learner

- beginner in domain,
- some experience,
- advanced.

Step 5 — Generation

- Fast,
- Standard,
- Deep.

Then Create + Generate.

## 14. Visual design

Recommended:

- restrained neutral palette,
- strong typography hierarchy,
- process lines and stage cards,
- minimal decorative gradients,
- consistent spacing,
- clear status badges.

The content is cognitively dense; visual design should reduce noise.

## 15. Responsive behavior

Desktop is primary.

Tablet:

- collapsible sidebar,
- vertical process flow.

Mobile:

- reading and learning supported,
- deep editing is secondary.

## 16. Keyboard shortcuts

Suggested:

```text
g o  → Overview
g l  → Learn
g s  → Sources
g v  → Versions
/    → Search
e    → Edit current section
```

Do not make shortcuts mandatory.

## 17. Loading states

Prefer skeletons for artifact reading.

Generation uses explicit progress state.

Avoid blocking full-screen spinners after the app shell loads.

## 18. Frontend stack

- Next.js App Router
- TypeScript strict mode
- Tailwind CSS
- shadcn/ui
- TanStack Query
- Zod for frontend runtime validation
- Mermaid or simple custom process rendering
- React Flow only for optional graph view, not required for V1

## 19. Frontend completion criteria

- all core routes exist,
- no dead navigation,
- responsive project reading,
- generation progress works,
- artifact renders from schema,
- inline editing works,
- Learn Mode persists progress,
- export is reachable,
- error and empty states implemented,
- Playwright flow passes.
