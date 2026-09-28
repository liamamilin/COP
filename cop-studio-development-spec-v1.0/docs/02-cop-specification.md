# 02 — COP Specification v0.1

## 1. Definition

COP (Concept–Operation Process) is a knowledge-production and learning paradigm for operational domains.

It organizes a domain as:

```text
Domain
↓
Goal
↓
Main Process
↓
Stage
↓
Concept × Operation
```

COP does not attempt to exhaustively represent a domain.

It attempts to preserve the most useful operational structure with low cognitive load.

## 2. Domain

A Domain is the scoped practice area addressed by the COP.

Examples:

- LangChain Agent Development
- Data visualization with ggplot2
- Git-based version-control workflow
- Docker application packaging

Bad scopes are either too broad or too narrow.

## 3. Goal

A Goal is an independent, valuable, verifiable capability outcome.

Good:

- Build a working Tool-Calling Agent.
- Produce a publication-ready multi-series plot.
- Package and run an application in Docker.

Weak:

- Learn LangChain.
- Understand Docker.
- Study visualization.

## 4. Zero State

The semantic default starting point is Zero State.

Zero State means:

> Do not assume domain-specific setup or completed prerequisites unless explicitly declared.

Every Main Process must be traceable back to Zero State, even if repeated setup is hidden through Shared Foundations.

## 5. Main Process

A Main Process is the primary path from Zero State or a Shared Foundation to a Goal.

```text
Start
↓
Stage
↓
Stage
↓
Stage
↓
Goal
```

Main Processes represent the core path, not every exception.

### Main Process split rule

Create a distinct Main Process when the target capability changes enough that the core Stage structure materially changes.

Use a Branch when only one Stage has an alternative implementation.

## 6. Stage

A Stage is a coherent unit inside a Main Process that achieves a local outcome.

```text
Stage
=
Local Goal
+
Concepts
+
Operations
```

A good Stage can usually be expressed as:

> Complete X to obtain Y.

## 7. Concept

A Concept is a stable, meaningful object category necessary for understanding or operating the current Domain.

Examples:

- Agent
- Tool
- Model
- Message
- Retriever
- Data Frame
- Plot
- Repository
- Commit

Not every noun is a first-class Concept.

A term should be promoted to Concept when misunderstanding it would materially damage the user’s mental model or execution.

## 8. Operation

An Operation is a meaningful action applied to one or more Concepts to advance the Process.

Examples:

- configure,
- initialize,
- invoke,
- bind,
- retrieve,
- transform,
- stage,
- commit,
- render.

Operations are not intended to enumerate every API call.

Low-level parameters and API syntax belong to Implementation Detail unless they materially affect the mental model.

## 9. Branch

### Alternative Branch

Different ways to complete the same Stage.

```text
Configure Model
├─ OpenAI-compatible provider
├─ Anthropic provider
└─ Local model
```

### Extension Branch

Adds capability to a base result.

```text
Basic Agent
├─ + Memory
├─ + Retrieval
└─ + Human-in-the-loop
```

## 10. Shared Foundation

Repeated Main Process prefixes are defined once.

```text
Shared Foundation:
Zero
→ Environment
→ Install framework
→ Configure provider
```

Later processes reference the foundation rather than repeating it.

Design principle:

> Semantically start from zero; visually start from the first meaningful difference.

## 11. Implementation Detail

Implementation Detail contains:

- parameters,
- exact commands,
- API signatures,
- provider-specific settings,
- optional edge cases.

It is expandable, not primary.

## 12. Mental Model

The COP should provide a compact explanation of how the system works as a whole.

The Mental Model should let the learner answer:

- What are the core objects?
- How do they interact?
- Why do the major Stages exist?
- Where would a new capability attach?
- Which part changes when the Goal changes?

## 13. Minimal Practice

A Main Process should preferably include one small practice that traverses the key structure.

The practice is successful when the user completes the Goal while touching the important Concepts and Operations.

## 14. Quality principle

A strong COP maximizes:

```text
Operational Value
× Mental Model Value
× Clarity
------------------------------
Cognitive Load
```

This is a design heuristic, not a mathematical scoring formula.

## 15. Failure modes

### Encyclopedia Failure

Many terms, no path.

### API Manual Failure

Many commands and parameters, no system model.

### Oversimplification Failure

The structure is so compressed that it cannot support action.

## 16. Validation levels

### L1 — Structural Validity

The hierarchy and relationships are coherent.

### L2 — Operational Validity

A user can follow the Main Process and achieve the Goal.

### L3 — Mental Model Validity

A user can reason about related cases that were not directly taught.

## 17. Canonical minimal form

```text
Domain
↓
Goal
↓
Main Process
↓
Stage
↓
Concept × Operation
```

Everything else exists to improve reuse, understanding, execution, or learning.
