# 19 — V1 Scope Freeze

## 1. Purpose

V1 is frozen around one complete loop:

```text
Produce COP
→ Manage COP
→ Learn COP
```

The objective is not feature breadth. The objective is a coherent product that proves the COP paradigm.

## 2. Must ship

### Produce

- Create project from topic/scope.
- Add source by pasted text.
- Upload TXT / Markdown / PDF.
- Add public HTTP/HTTPS URL.
- Configure one OpenAI-compatible model endpoint.
- Provide deterministic Mock Provider.
- Run persisted COP Harness.
- Stream generation progress.
- Produce validated COP candidate.
- Retry/repair malformed structured output.

### Manage

- Project list.
- COP overview.
- Goal / Main Process / Stage views.
- Concept / Operation views.
- Source manager.
- One active draft.
- Manual field editing.
- Partial AI refinement at Goal / Process / Stage level.
- Candidate patch preview.
- Immutable published versions.
- Version history.
- JSON and Markdown export.

### Learn

- Choose Goal.
- See full Main Process before entering a Stage.
- Move Stage-by-Stage.
- See local goal, why it exists, Concepts, Operations, example, implementation detail.
- Mark Stage complete.
- Complete Minimal Practice.
- View checkpoint questions.
- Persist progress.

### Operate

- Settings UI.
- Provider connection test.
- Generation defaults.
- Light / dark / system appearance.
- Docker Compose.
- Automated tests.
- Backup/restore documentation.

## 3. Explicitly not V1

Do not implement unless all frozen acceptance tests already pass:

- accounts,
- teams,
- collaboration,
- public sharing,
- cloud sync,
- mobile-native app,
- browser extension,
- GitHub repository ingestion,
- Google Drive / Notion / Slack ingestion,
- semantic/vector search,
- spaced repetition,
- adaptive curriculum,
- chat assistant embedded on every page,
- graph database,
- generic ontology editor,
- drag-and-drop process graph editing,
- multi-provider model routing,
- automatic model cost optimization,
- marketplace,
- payment,
- analytics dashboard,
- rich WYSIWYG document editor,
- PDF export,
- WebSocket infrastructure,
- Redis/Celery,
- Kubernetes deployment.

## 4. Deliberate technical simplifications

### Database

PostgreSQL 16+ is the only normative V1 database.

Reason:

- one migration behavior,
- one job-claiming behavior,
- JSONB support,
- no SQLite concurrency branch.

### Queue

Use the PostgreSQL-backed `generation_runs` queue.

Do not introduce Redis in V1.

### Artifact persistence

Store the versioned COP as JSONB.

Do not normalize every Concept/Stage into relational tables.

### UI visualization

Use hierarchical process UI.

Do not make React Flow or a node graph a dependency for V1.

### Authentication

Local V1 binds to localhost and has no account system.

If LAN binding is added, require a local access token.

## 5. Scope change rule

A proposed feature enters V1 only if removing it makes one of these impossible:

```text
Generate a useful COP
Manage/revise that COP
Learn through that COP
Export/retain that COP
```

Otherwise it is post-V1.
