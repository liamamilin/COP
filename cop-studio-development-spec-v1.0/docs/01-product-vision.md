# 01 — Product Vision

## 1. Product thesis

Most technical and practical knowledge is presented as documentation, chapters, API references, tutorials, or disconnected topics.

This creates a common problem:

> The learner receives information before receiving a usable structure.

COP Studio reverses that order.

It first identifies:

```text
Goal
↓
Main Process
↓
Stage
↓
Concept × Operation
```

and only then attaches detail.

The product aims to reduce **time to usable mental model**.

## 2. User problem

A user approaching a new domain often experiences:

- too many pages,
- too many terms,
- unclear learning order,
- examples without a system model,
- API knowledge without architectural understanding,
- repeated setup instructions,
- difficulty identifying what matters,
- difficulty transferring learning to new cases.

Example:

A user wants to learn LangChain.

Traditional experience:

```text
Agents
Models
Messages
Tools
Middleware
Memory
Runtime
Structured Output
Retrieval
LangGraph
...
```

COP experience:

```text
Goal: Build a Tool-Calling Agent

Shared Foundation
↓
Configure Model
↓
Define Tool
↓
Construct Agent
↓
Execute
↓
Verify
↓
Working Tool-Calling Agent
```

The Concepts and Operations are learned inside the Stage where they matter.

## 3. Primary user

V1 primary user:

- technically literate,
- frequently learns frameworks, tools, systems, or professional methods,
- willing to use AI,
- values structure over exhaustive reference material,
- wants to get operational quickly.

V1 is especially suitable for:

- developers,
- data scientists,
- AI engineers,
- researchers,
- advanced self-learners,
- technical writers,
- instructors.

## 4. Jobs to be done

### Knowledge production

> “Given a topic or a set of sources, produce a compact but useful COP.”

### Orientation

> “Show me what this domain is for and the main things I can accomplish.”

### Learning

> “Take me from zero through a Main Process without drowning me in unrelated detail.”

### Mental-model formation

> “Help me understand how the pieces fit so that I can reason about cases you did not directly teach me.”

### Knowledge management

> “Let me maintain, revise, version, search, and export COP material.”

## 5. Non-goals

V1 is not:

- a generic note-taking application,
- a general-purpose ontology editor,
- a full graph database UI,
- a universal LMS,
- an academic knowledge representation language,
- a citation manager,
- a generic chat-with-documents tool,
- a complete coding IDE,
- a social knowledge network.

## 6. Product success

The strongest product metric is:

> **Time to Mental Model**

Practical proxies:

- time from project creation to usable COP,
- percentage of generated Main Processes accepted with minor edits,
- percentage of users who can complete a minimal practice,
- number of COPs revisited after generation,
- percentage of sessions entering Learn Mode,
- time to first completed Goal,
- percentage of users able to answer transfer questions.

## 7. Product philosophy

### Operational sufficiency

A useful 30% of the domain is better than a complete but unusable 100%.

### Structured compression

COP is not a summary.

Summary:

```text
10,000 words → 1,000 words
```

COP:

```text
Raw knowledge
→ operational structure
```

### Progressive disclosure

Default view:

```text
Overview
→ Goal
→ Main Process
→ Stage
```

Details appear only when opened:

```text
Concept
Operation
Implementation Detail
Evidence
Example
```

### Source-aware, not source-bound

Sources support COP construction.

The final artifact should be organized around the domain and user goals, not around source chapter order.

## 8. Working product name

**COP Studio**

Alternative later names may be considered, but the codebase should use `cop-studio` until a branding decision is made.
