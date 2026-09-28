# Reference COP — LangChain Agent Development

This is the primary reference artifact for COP Studio V1.

It is intentionally **not exhaustive**. It demonstrates what “high-value operational sufficiency” looks like.

## Why this reference was chosen

LangChain is a useful stress test because:

- it has many Concepts,
- its official documentation is broad,
- users can easily become lost in component lists,
- the current framework explicitly centers `create_agent`, a model loop, tools, middleware, and persistence,
- different Goals naturally create different Main Processes.

## Reference sources checked on 2026-09-28

Official LangChain documentation:

- `https://docs.langchain.com/oss/python/langchain/overview`
- `https://docs.langchain.com/oss/python/langchain/agents`
- `https://docs.langchain.com/oss/python/langchain/tools`
- `https://docs.langchain.com/oss/python/langchain/short-term-memory`
- `https://docs.langchain.com/oss/python/deepagents/retrieval`
- `https://docs.langchain.com/oss/python/langchain/middleware/overview`
- `https://docs.langchain.com/oss/python/langchain/structured-output`

The official overview currently describes `create_agent` as a minimal configurable agent harness and summarizes the idea as “Agent = Model + Harness.” The Agents documentation describes the core loop as a model calling tools until the task is complete. Middleware is documented as the mechanism for controlling/customizing behavior around that loop. Retrieval documentation distinguishes 2-step, agentic, and hybrid RAG patterns.

## Reference Goal set

```text
1. Basic Agent
2. Tool-Calling Agent
3. Stateful Conversational Agent
4. Agentic RAG Agent
5. Controlled Agent with Middleware
```

This is not a claim that these are the only valid LangChain Goals.

They are selected because together they demonstrate:

- a minimal foundation,
- a core tool loop,
- state as an added capability,
- retrieval as a meaningful process variant,
- middleware as a harness extension point.

## Shared Foundation

```text
Zero
↓
Install LangChain/provider integration
↓
Configure model
```

It appears once.

Every Main Process remains semantically traceable to zero.

## Product usage

The frontend seed data should render this artifact.

The Harness golden-set tests should compare generated structure against it semantically, not by exact strings.

Expected invariant examples:

- `Model`, `Agent`, `Harness`, `Tool` should appear as structural Concepts.
- Tool-calling process should contain a Tool definition Stage.
- Stateful process should include persistence/state continuity.
- Agentic RAG should expose retrieval capability and verify retrieved knowledge use.
- Middleware should be represented as Harness control, not as a separate model.

## What the reference deliberately excludes

- every provider,
- every tool API,
- every middleware class,
- full LangGraph API,
- deployment details,
- LangSmith workflow details,
- every RAG implementation.

Those belong to branches, implementation detail, or separate COP scopes.
