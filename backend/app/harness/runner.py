"""Harness runner.

Owns the step pipeline, checkpoint persistence, event emission, provider
reliability, and cancellation. Steps stay ignorant of all three so they remain
unit-testable against a fake provider.

Terminal state mapping:

- every step successful       -> `completed`
- validation could not finish -> `needs_attention` (checkpoints preserved)
- fatal step error            -> `failed`
- user cancellation           -> `cancelled`
"""

import asyncio
import logging
import time
from typing import Any

from app.core.errors import HarnessError
from app.harness.context import (
    HarnessContext,
    HarnessEvent,
    HarnessStep,
    StepResult,
    StepStatus,
)
from app.harness.providers.base import LLMProvider, ProviderError
from app.harness.steps import STEP_LABELS, STEP_PIPELINE, TARGETED_PIPELINE
from app.harness.steps.h120_validate import resolve_schema_path, validate

logger = logging.getLogger("cop.harness")

MAX_STEP_ATTEMPTS = 3
RETRY_BASE_DELAY_SECONDS = 0.5


class RunStore:
    """Persistence surface the runner needs. Implemented by `jobs.runner`."""

    def emit(self, run_id: str, events: list[HarnessEvent]) -> None:
        raise NotImplementedError

    def save_checkpoint(self, run_id: str, context: HarnessContext) -> None:
        raise NotImplementedError

    def heartbeat(self, run_id: str) -> None:
        raise NotImplementedError

    def metrics(self, run_id: str) -> dict[str, Any]:
        raise NotImplementedError

    def is_cancelled(self, run_id: str) -> bool:
        raise NotImplementedError

    def set_candidate(self, run_id: str, artifact: dict[str, Any] | None) -> None:
        raise NotImplementedError


class HarnessServicesImpl:
    """Provider wrapper that adds retries, latency metrics, and cancellation."""

    def __init__(self, provider: LLMProvider, run_id: str, store: RunStore) -> None:
        self._provider = provider
        self._run_id = run_id
        self._store = store
        self.calls: list[dict[str, Any]] = []

    async def complete_structured(
        self, *, system_prompt: str, user_prompt: str, schema: dict[str, Any]
    ) -> dict[str, Any]:
        started = time.monotonic()
        last_error: ProviderError | None = None
        for attempt in range(1, MAX_STEP_ATTEMPTS + 1):
            try:
                result = await self._provider.generate_structured(
                    system_prompt=system_prompt, user_prompt=user_prompt, schema=schema
                )
                self.calls.append(
                    {
                        "step": schema.get("title"),
                        "attempts": attempt,
                        "latency_ms": int((time.monotonic() - started) * 1000),
                    }
                )
                return result
            except ProviderError as exc:
                last_error = exc
                if not exc.retryable or attempt >= MAX_STEP_ATTEMPTS:
                    break
                # Back off so a rate-limited provider is not hammered.
                await asyncio.sleep(RETRY_BASE_DELAY_SECONDS * attempt)
        assert last_error is not None
        raise last_error

    async def complete_text(self, *, system_prompt: str, user_prompt: str) -> str:
        return await self._provider.generate_text(
            system_prompt=system_prompt, user_prompt=user_prompt
        )

    def emit(self, event: HarnessEvent) -> None:
        self._store.emit(self._run_id, [event])

    def is_cancelled(self) -> bool:
        return self._store.is_cancelled(self._run_id)


class HarnessOutcome:
    """Terminal result of a pipeline execution.

    `provider_calls` comes from the services instance the pipeline actually used.
    The runner owns that instance internally, so it is reported here rather than
    leaving each caller to guess; otherwise call metrics would silently read zero.
    """

    def __init__(
        self,
        status: str,
        context: HarnessContext,
        provider_calls: list[dict[str, Any]] | None = None,
        error_code: str | None = None,
        error_message: str | None = None,
    ) -> None:
        self.status = status
        self.context = context
        self.provider_calls = provider_calls or []
        self.error_code = error_code
        self.error_message = error_message


async def run_pipeline(
    context: HarnessContext,
    provider: LLMProvider,
    store: RunStore,
) -> HarnessOutcome:
    """Execute every step in order, persisting a checkpoint after each.

    A run that named a target takes the short refinement path instead. The
    distinction is made here rather than in the worker so both callers, and the
    tests, get the same routing from the same context.
    """
    if context.partial_target:
        return await run_targeted_pipeline(context, provider, store)
    return await _execute_steps(context, provider, store, STEP_PIPELINE)


async def run_targeted_pipeline(
    context: HarnessContext,
    provider: LLMProvider,
    store: RunStore,
) -> HarnessOutcome:
    """Review what already exists and propose a patch for one entity.

    The artifact is loaded from the run's base, never regenerated, so a
    refinement cannot quietly rewrite content the user never asked about.
    """
    return await _execute_steps(context, provider, store, TARGETED_PIPELINE)


async def _execute_steps(
    context: HarnessContext,
    provider: LLMProvider,
    store: RunStore,
    pipeline: tuple[HarnessStep, ...],
) -> HarnessOutcome:
    services = HarnessServicesImpl(provider, context.run_id, store)
    store.emit(context.run_id, [HarnessEvent("run.started", {"steps": len(pipeline)})])

    context.settings.setdefault("schema_path", str(resolve_schema_path() or ""))

    # Resume by skipping individually satisfied steps rather than slicing the
    # pipeline. Slicing at the first incomplete step would re-run later steps
    # whose output is already checkpointed, overwriting it: a retry that has
    # scope and goals would regenerate its scope and disagree with the goals.
    steps = tuple(step for step in pipeline if not _step_satisfied(step.name, context))
    resumed_from = steps[0].name if steps and len(steps) < len(pipeline) else None
    if resumed_from is not None:
        store.emit(
            context.run_id,
            [
                HarnessEvent(
                    "run.resumed",
                    {"from_step": resumed_from, "checkpoints": context.completed_checkpoints()},
                )
            ],
        )

    for step in steps:
        if store.is_cancelled(context.run_id):
            return HarnessOutcome("cancelled", context, services.calls)

        store.emit(
            context.run_id,
            [
                HarnessEvent(
                    "step.started",
                    {"step": step.name, "label": STEP_LABELS.get(step.name, step.name)},
                )
            ],
        )
        try:
            result = await step.execute(context, services)
        except HarnessError as exc:
            if exc.code == "GENERATION_CANCELLED":
                return HarnessOutcome("cancelled", context, services.calls)
            return _fail(context, services, store, step, exc.code, exc.message)
        except ProviderError as exc:
            return _fail(context, services, store, step, exc.code, str(exc))
        except Exception as exc:  # noqa: BLE001 - never lose the checkpoint
            logger.exception("Harness step %s crashed", step.name)
            return _fail(
                context, services, store, step, "HARNESS_STEP_CRASHED", f"{step.name} failed: {exc}"
            )

        store.emit(context.run_id, result.events)
        if result.warnings:
            store.emit(
                context.run_id,
                [HarnessEvent("step.warning", {"step": step.name, "warnings": result.warnings})],
            )
        if result.checkpoint_patch:
            context.apply(result.checkpoint_patch)
        store.save_checkpoint(context.run_id, context)
        store.heartbeat(context.run_id)

        if result.status is StepStatus.FATAL_FAILURE:
            code, message = _fatal_detail(result)
            return _fail(context, services, store, step, code, message)
        if result.status is StepStatus.RETRYABLE_FAILURE:
            store.emit(
                context.run_id,
                [HarnessEvent("run.retrying", {"step": step.name})],
            )

    return HarnessOutcome(_final_status(context), context, services.calls)


def _fail(
    context: HarnessContext,
    services: HarnessServicesImpl,
    store: RunStore,
    step: HarnessStep,
    code: str,
    message: str,
) -> HarnessOutcome:
    """Record a terminal failure with its real cause attached.

    The checkpoint is saved first: a run that failed still holds every step that
    did succeed, and the user needs that work to be resumable.
    """
    store.save_checkpoint(context.run_id, context)
    store.emit(
        context.run_id,
        [HarnessEvent("run.failed", {"step": step.name, "code": code, "message": message})],
    )
    return HarnessOutcome("failed", context, services.calls, code, message)


def _fatal_detail(result: StepResult) -> tuple[str, str]:
    """Extract the code and message a step reported when it failed fatally."""
    for event in result.events:
        if event.event_type == "step.failed":
            payload = event.payload
            return (
                str(payload.get("code", "HARNESS_STEP_FAILED")),
                str(payload.get("message", "The Harness step failed")),
            )
    return "HARNESS_STEP_FAILED", "The Harness step failed"


def _step_satisfied(name: str, context: HarnessContext) -> bool:
    """True when this step's output is already checkpointed.

    H120 and H130 always return False. They are the validation tail: their job
    is to decide whether the artifact is publishable, so re-entering a run that
    already holds an artifact must re-run them rather than trust the stored one.
    """
    if name == "H140":
        # A proposal is cheap to re-derive and stale the moment the draft moves,
        # so a resumed refinement always asks again rather than replaying an
        # answer to a question about content that has since changed.
        return False
    if name in {"H120", "H130"}:
        return False
    return {
        "H00": context.intake is not None,
        "H10": context.scope_result is not None,
        "H20": context.research_brief is not None,
        "H30": bool(context.goals),
        "H40": bool(context.process_drafts),
        "H50": bool(context.stage_drafts),
        "H60": bool(context.concepts) and bool(context.operations),
        "H70": bool(context.process_starts),
        "H80": context.mental_model is not None,
        "H90": context.artifact is not None,
        "H100": context.critic_report is not None,
        "H110": context.critic_report is not None,
    }.get(name, False)


def _final_status(context: HarnessContext) -> str:
    # A targeted run produces a patch, not a candidate artifact. Judging it by
    # artifact validation would report `failed` for a run that did exactly what
    # it was asked, because it never produced one.
    if context.partial_target:
        return "completed" if context.candidate_patch is not None else "failed"
    if context.artifact is None:
        return "failed"
    if validate(context.artifact, resolve_schema_path(context.settings.get("schema_path"))):
        return "needs_attention"
    return "completed"


def build_metrics(
    context: HarnessContext, provider_calls: list[dict[str, Any]], started: float
) -> dict[str, Any]:
    artifact = context.artifact or {}
    return {
        "provider_calls": len(provider_calls),
        "retried_calls": sum(1 for call in provider_calls if call.get("attempts", 1) > 1),
        "total_latency_ms": int((time.monotonic() - started) * 1000),
        "goals": len(artifact.get("goals") or []),
        "main_processes": len(artifact.get("main_processes") or []),
        "stages": len(artifact.get("stages") or []),
        "concepts": len(artifact.get("concepts") or []),
        "operations": len(artifact.get("operations") or []),
        "practices": len(artifact.get("practices") or []),
        "checkpoints": context.completed_checkpoints(),
        "calls": provider_calls,
    }
