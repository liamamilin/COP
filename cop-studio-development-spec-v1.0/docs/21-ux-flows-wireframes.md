# 21 — UX Flows and Wireframes

These wireframes are behavioral specifications, not final visual design.

## 1. Home

```text
┌─────────────────────────────────────────────────────────┐
│ COP Studio                               Settings       │
├─────────────────────────────────────────────────────────┤
│ Your COPs                               [+ New COP]      │
│                                                         │
│ ┌─────────────────────────────────────────────────────┐ │
│ │ LangChain Agent Development          v4             │ │
│ │ 4 Goals · Learning 42% · Updated today             │ │
│ │ Continue: Stateful Agent → Configure persistence    │ │
│ └─────────────────────────────────────────────────────┘ │
│                                                         │
│ Empty state:                                            │
│ Turn a topic or source set into a learnable COP.       │
│                                         [Create COP]    │
└─────────────────────────────────────────────────────────┘
```

Primary action: create/continue, not browse settings.

## 2. New COP wizard

### Step 1 — Intent

```text
What do you want to become able to do?

[ LangChain Agent Development                         ]

Optional scope:
[ Build common agents and understand how components fit ]

Current experience:
(o) New to this domain
( ) Some experience
( ) Advanced
```

### Step 2 — Sources

```text
Sources are optional.

[ Paste Text ] [ Upload ] [ Add URL ]

Added:
✓ Official overview
✓ Agent docs
```

### Step 3 — Generation

```text
Generation
(o) Standard — recommended
( ) Fast
( ) Deep

Language: Chinese
Practices: Priority processes
Evidence: Key claims

                        [Create and Generate]
```

## 3. Generation

```text
┌─────────────────────────────────────────────────────┐
│ Building your COP                                  │
│                                                     │
│ ✓ Defining scope                                   │
│ ✓ Understanding sources                            │
│ ✓ Finding high-value goals                         │
│ ● Building main processes                          │
│ ○ Extracting concepts and operations               │
│ ○ Compressing repeated foundations                 │
│ ○ Generating learning material                     │
│ ○ Reviewing quality                                │
│                                                     │
│ Current finding: 4 Goals identified                │
│                                                     │
│ [Cancel]                                           │
└─────────────────────────────────────────────────────┘
```

Do not expose hidden reasoning or raw model tokens.

Useful partial structure may appear after a step is checkpointed, but it must be labeled Draft.

## 4. Project Overview

```text
┌─────────────────────────────────────────────────────────────┐
│ LangChain Agent Development        v3 Published             │
│ [Refine] [Learn] [Export]                                  │
├───────────────┬─────────────────────────────────────────────┤
│ Overview      │ Mental Model                                │
│ Goals         │                                             │
│ Processes     │ User → Agent → Model ↔ Tools → Response    │
│ Concepts      │                                             │
│ Sources       │ ─────────────────────────────────────────   │
│ Versions      │ Goals                                       │
│               │                                             │
│               │ 1. Basic Agent                [Start]       │
│               │ 2. Tool-Calling Agent         [Start]       │
│               │ 3. Stateful Agent             [Start]       │
│               │ 4. Agentic RAG                [Start]       │
│               │                                             │
│               │ Shared Foundation                           │
│               │ Environment → Model configuration           │
└───────────────┴─────────────────────────────────────────────┘
```

## 5. Goal / Main Process

```text
Goal: Build a Tool-Calling Agent
Outcome: Agent can select and invoke an external tool.

[Foundation]
     ↓
[Define Tool] → [Construct Agent] → [Run] → [Verify]
     │
     └ Alternative: function / tool object

Minimal Practice: Weather lookup agent

[Start Learn Mode]
```

The Process must be visible before details.

## 6. Stage Detail

```text
Stage 2 of 4 — Define Tool

LOCAL GOAL
Create a capability the agent can call.

WHY THIS EXISTS
The model can generate output, but a Tool gives the system an
explicit external capability.

CONCEPTS
[Tool] [Schema]

OPERATIONS
[Define] [Describe]

EXAMPLE
Weather lookup tool...

▶ Implementation details
▶ Evidence
▶ Alternatives

[Refine this Stage]
```

## 7. AI refinement

```text
Refine Stage

Instruction:
[ Make this more suitable for a beginner, but keep it concise. ]

                      [Generate candidate]

Current                           Candidate
----------------------            ----------------------
...                               ...

[Reject]                     [Accept into Draft]
```

Accept never publishes automatically.

## 8. Draft mode

When a Draft exists:

```text
Draft based on v3 · Unsaved to history

[Discard Draft] [Validate] [Publish v4]
```

Manual field saves persist to Draft continuously, but publishing is explicit.

## 9. Learn Mode

```text
┌────────────────────────────────────────────────────────────┐
│ Tool-Calling Agent       Stage 2 / 4       25%             │
│ ← Exit Learn Mode                                           │
├────────────────────────────────────────────────────────────┤
│ Process                                                     │
│ Foundation → Tool → Agent → Run → Verify                   │
│                 ▲                                          │
│                                                            │
│ DEFINE TOOL                                                │
│ Goal: create a callable external capability.               │
│                                                            │
│ Why it matters...                                          │
│                                                            │
│ Concept: Tool                                              │
│ Operation: Define                                          │
│                                                            │
│ [Show implementation]                                      │
│                                                            │
│ [Previous]            [Mark complete & Next]               │
└────────────────────────────────────────────────────────────┘
```

At process end:

```text
Goal complete

Practice: build a weather lookup agent

Checkpoint:
- Why is Tool separate from Model?
- Where would Memory attach?
- What changes if no Tool is needed?

[Explore next Goal]
```

## 10. Error states

### Provider missing

```text
Generation cannot start.
No model provider is configured.

[Open Provider Settings]
```

### Structured output repair exhausted

```text
The source analysis completed, but the generated COP still has
invalid references after repair.

Your work was kept through the last valid checkpoint.

[Retry finalization] [Inspect run]
```

### Source extraction warning

```text
PDF text extraction looks incomplete.
You can continue, replace the source, or inspect extracted text.

[Inspect] [Continue anyway]
```

## 11. UX invariants

At all times:

- published content and draft content are visually distinguishable,
- AI candidates are not silently accepted,
- a Main Process can be understood without opening every Stage,
- low-level implementation is collapsed by default,
- user progress is separate from artifact versioning,
- generation failure never erases a published version.
