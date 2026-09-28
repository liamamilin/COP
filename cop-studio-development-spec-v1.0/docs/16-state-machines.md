# 16 — State Machines

This document removes ambiguity around lifecycle behavior.

## 1. Source state

```text
created
↓
processing
├─→ ready
└─→ failed
```

Retry:

```text
failed → processing
ready  → processing
```

Deleting a source removes it from future runs but does not invalidate already published COP versions.

## 2. Generation run state

```text
queued
↓
running
├─→ completed
├─→ needs_attention
├─→ failed
└─→ cancelled
```

### queued

Run exists but has not been claimed by a worker.

### running

A worker owns the run and updates heartbeat.

### needs_attention

Useful partial work exists but automatic repair could not finish safely.

### completed

A valid candidate artifact or patch was produced.

### failed

No publishable candidate was produced.

### cancelled

User cancellation was acknowledged.

Terminal states:

```text
completed
needs_attention
failed
cancelled
```

## 3. Worker recovery

A `running` job is stale when heartbeat exceeds the configured threshold.

Recovery:

```text
running(stale)
→ queued
```

Only retry automatically when the run is marked retry-safe.

Persist Harness checkpoints so recovery does not restart from Step 0 unnecessarily.

## 4. Draft/version state

```text
Published Version
↓ create draft
Draft
├─ edit
├─ accept AI patch
├─ reject AI patch
└─ publish
      ↓
New Published Version
```

Published versions are immutable.

A project may have at most one active draft in V1.

## 5. AI candidate patch state

```text
generating
↓
ready
├─→ accepted
├─→ rejected
└─→ expired
```

Accepting applies the patch to the active draft, never directly to a published version.

## 6. Learning state

Per Stage:

```text
not_started
↓
in_progress
↓
completed
```

Allow:

```text
completed → in_progress
```

when the user revisits/reset progress.

Goal completion is derived from:

- all required Stages completed,
- or explicit user completion if project settings permit.

## 7. Project state

```text
active
archived
deleted
```

`deleted` should be soft-delete first. Permanent cleanup can be a separate maintenance action.

## 8. UI behavior

Every asynchronous state must have:

- visible status,
- retry where meaningful,
- clear terminal state,
- no silent transitions that lose user work.
