"""Checkpoint recovery policy. No database, HTTP, or provider dependencies."""

from dataclasses import dataclass
from typing import Any

from app.harness.context import HarnessContext
from app.harness.steps import STEP_PIPELINE


@dataclass(frozen=True)
class RecoveryPlan:
    allowed: bool
    reason: str
    from_step: str | None = None
    completed_steps: tuple[str, ...] = ()


def checkpoint_plan(checkpoint: dict[str, Any]) -> RecoveryPlan:
    """Only explicit, contiguous, complete step outputs may be reused manually.

    Old crash-recovery heuristics remain in the runner for legacy checkpoints.
    A user-facing resume must not silently guess whether partial work finished.
    The validation tail always runs again.
    """
    try:
        ctx = HarnessContext.from_dict(checkpoint)
        names = [step.name for step in STEP_PIPELINE]
        completed = ctx.completed_steps
        if not completed or completed != names[: len(completed)]:
            return RecoveryPlan(
                False, "The checkpoint has no continuous completion record. Start over to continue."
            )
        if not isinstance(ctx.input, dict) or not isinstance(ctx.settings, dict):
            raise ValueError("Invalid input/settings snapshot")
        if not isinstance(ctx.source_bundle, list):
            raise ValueError("Invalid source snapshot")
        if "source_bundle" not in checkpoint or not ctx.input or not ctx.settings:
            return RecoveryPlan(
                False,
                "The original input, settings, or source snapshot is incomplete. "
                "Start over to continue.",
            )

        # Check full collections, not merely whether one item exists.
        process_keys = {p["key"] for p in ctx.process_drafts}
        goal_keys = {g["key"] for g in ctx.goals}
        stage_keys = {s["key"] for p in ctx.process_drafts for s in p["stages"]}
        enriched_keys = {s["key"] for s in ctx.stage_drafts}
        valid = {
            "H00": isinstance(ctx.intake, dict)
            and bool(ctx.intake.get("topic") or ctx.source_bundle),
            "H10": isinstance(ctx.scope_result, dict)
            and all(ctx.scope_result.get(k) for k in ("domain", "scope", "target_user")),
            "H20": isinstance(ctx.research_brief, dict) and bool(ctx.research_brief),
            "H30": bool(goal_keys) and len(goal_keys) == len(ctx.goals),
            "H40": bool(stage_keys)
            and len(process_keys) == len(ctx.process_drafts)
            and {p["goal_key"] for p in ctx.process_drafts} == goal_keys,
            "H50": bool(stage_keys)
            and enriched_keys == stage_keys
            and len(enriched_keys) == len(ctx.stage_drafts),
            "H60": bool(ctx.concepts)
            and bool(ctx.operations)
            and set(ctx.stage_bindings) == stage_keys
            and set(ctx.bound_stage_keys) == stage_keys,
            "H70": bool(process_keys)
            and set(ctx.process_starts) == process_keys
            and set(ctx.process_stage_keys) == process_keys,
            "H80": isinstance(ctx.mental_model, dict) and bool(ctx.mental_model),
            "H90": isinstance(ctx.artifact, dict) and bool(ctx.artifact),
            "H100": isinstance(ctx.critic_report, dict),
            "H110": isinstance(ctx.critic_report, dict) and bool(ctx.artifact),
            "H120": isinstance(ctx.artifact, dict) and bool(ctx.artifact),
            "H130": isinstance(ctx.artifact, dict) and bool(ctx.artifact),
        }
        for name in completed:
            if not valid[name]:
                return RecoveryPlan(
                    False, f"The {name} checkpoint is incomplete. Start over to continue."
                )
        reusable = tuple(name for name in completed if name not in {"H120", "H130"})
        return RecoveryPlan(True, "", names[len(reusable)], reusable)
    except (TypeError, ValueError, KeyError, AttributeError):
        return RecoveryPlan(
            False, "The checkpoint is damaged or incompatible. Start over to continue."
        )


def recovery_plan(
    *,
    status: str,
    retry_safe: bool,
    targeted: bool,
    error_code: str | None,
    checkpoint: dict[str, Any],
) -> RecoveryPlan:
    if status != "failed":
        return RecoveryPlan(False, "Only failed generation runs can be resumed.")
    if not retry_safe or targeted:
        return RecoveryPlan(False, "This run cannot be resumed safely. Start over to continue.")
    if error_code not in {
        "PROVIDER_TIMEOUT",
        "PROVIDER_UNAVAILABLE",
        "PROVIDER_RATE_LIMITED",
        "PROVIDER_INVALID_OUTPUT",
        "PROVIDER_OUTPUT_TRUNCATED",
    }:
        return RecoveryPlan(False, "Resolve the underlying error before starting another run.")
    return checkpoint_plan(checkpoint)
