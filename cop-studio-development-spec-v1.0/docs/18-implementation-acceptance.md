# 18 — Implementation Acceptance Checklist

The coding agent should use this as the final V1 gate.

## Repository

- [ ] Root README exists.
- [ ] `.env.example` exists.
- [ ] Docker Compose exists.
- [ ] Frontend, API, worker, and database start successfully.
- [ ] No real credentials are committed.
- [ ] Lint and test commands are documented.

## Project lifecycle

- [ ] Create project.
- [ ] Edit project metadata.
- [ ] Archive/delete project.
- [ ] Project list survives restart.

## Sources

- [ ] Paste text.
- [ ] Upload TXT.
- [ ] Upload Markdown.
- [ ] Upload PDF.
- [ ] Add URL.
- [ ] Show processing state.
- [ ] Preview extracted text.
- [ ] Retry failed extraction.

## Settings

- [ ] Configure OpenAI-compatible provider.
- [ ] Mask stored API key.
- [ ] Test provider connection.
- [ ] Configure generation mode.
- [ ] Project overrides work.
- [ ] Mock provider selectable in development/test mode.

## Harness

- [ ] Full generation run can be created.
- [ ] Worker claims run.
- [ ] Progress events stream.
- [ ] Checkpoints persist.
- [ ] Valid COP artifact produced.
- [ ] Invalid model output triggers repair.
- [ ] Cancellation works.
- [ ] Failure produces actionable error.
- [ ] Run can survive API restart.

## COP artifact

- [ ] Overview renders.
- [ ] Mental model renders.
- [ ] Goal Map renders.
- [ ] Shared Foundation renders.
- [ ] Main Process renders.
- [ ] Stages render.
- [ ] Concepts render.
- [ ] Operations render.
- [ ] Branches render.
- [ ] Practices render.
- [ ] Expansion Map renders.

## Editing and versions

- [ ] Create draft.
- [ ] Inline edit Stage.
- [ ] Validate draft.
- [ ] Publish new version.
- [ ] Published version immutable.
- [ ] Version list works.
- [ ] Partial AI refinement returns candidate patch.
- [ ] Candidate patch can be accepted/rejected.

## Learn Mode

- [ ] Select Goal.
- [ ] Move through Stages.
- [ ] View Concept/Operation details.
- [ ] Expand implementation detail.
- [ ] Mark Stage complete.
- [ ] Progress survives restart.
- [ ] Practice visible.
- [ ] Checkpoint visible.
- [ ] Goal completion state visible.

## Export

- [ ] Export JSON.
- [ ] Export single Markdown.
- [ ] Export Markdown bundle.
- [ ] Exported bundle is readable without the application.

## Error handling

- [ ] Provider auth failure.
- [ ] Provider rate limit.
- [ ] Invalid structured output.
- [ ] Bad PDF.
- [ ] Unreachable URL.
- [ ] Worker crash/stale job.
- [ ] Cancelled run.
- [ ] Invalid draft publish.
- [ ] Missing source file.

## Quality

- [ ] No dead buttons.
- [ ] No placeholder-only core screen.
- [ ] Keyboard navigation works for main flows.
- [ ] Dark/light/system appearance works.
- [ ] Main Process remains visible and readable.
- [ ] Large fixture artifact remains responsive.

## Final end-to-end acceptance

On a clean machine:

```text
git clone
↓
configure .env
↓
docker compose up
↓
open app
↓
create project
↓
paste source
↓
use mock provider
↓
generate COP
↓
publish
↓
learn one Stage
↓
export Markdown
```

The sequence must complete without editing application source code.
