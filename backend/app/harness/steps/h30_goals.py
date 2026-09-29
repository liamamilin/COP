"""H30 — Extract Goals.

Identifies high-value, verifiable capability outcomes. Each Goal must be large
enough to justify its own Main Process.
"""

from typing import Any

from app.core.errors import HarnessError
from app.harness.context import HarnessContext, HarnessEvent, StepResult
from app.harness.prompts import build_goals_prompt
from app.harness.schemas import GOALS_SCHEMA

VAGUE_PREFIXES = ("learn ", "understand ", "study ", "know ", "familiarize")
DEPTH_TARGETS = {"fast": (2, 4), "standard": (3, 7), "deep": (5, 9)}


def quality_gate(goals: list[dict[str, Any]], depth: str) -> list[str]:
    """Return warnings for goals that fail the capability-outcome bar."""
    warnings: list[str] = []
    for goal in goals:
        title = str(goal.get("title", "")).strip().lower()
        outcome = str(goal.get("outcome", "")).strip()
        if title.startswith(VAGUE_PREFIXES):
            warnings.append(f"Goal '{goal.get('title')}' describes learning rather than a result")
        if len(outcome) < 12:
            warnings.append(f"Goal '{goal.get('title')}' has no verifiable outcome")
    low, high = DEPTH_TARGETS.get(depth, DEPTH_TARGETS["standard"])
    if len(goals) < low:
        warnings.append(f"Only {len(goals)} Goals were proposed; {depth} mode targets {low}-{high}")
    elif len(goals) > high:
        warnings.append(f"{len(goals)} Goals were proposed; {depth} mode targets {low}-{high}")
    return warnings


class GoalExtractionStep:
    name = "H30"

    async def execute(self, ctx: HarnessContext, services: Any) -> StepResult:
        scope = ctx.require("scope_result")
        brief = ctx.require("research_brief")
        language = ctx.settings.get("language", "auto")
        depth = ctx.settings.get("generation_depth", "standard")

        system, user = build_goals_prompt(
            scope=scope,
            brief=brief,
            requested_outcomes=list(ctx.input.get("target_outcomes") or []),
            depth=depth,
            language=language,
        )
        payload = await services.complete_structured(
            system_prompt=system, user_prompt=user, schema=GOALS_SCHEMA
        )

        raw_goals = payload.get("goals") or []
        goals: list[dict[str, Any]] = []
        seen_keys: set[str] = set()
        for index, raw in enumerate(raw_goals, start=1):
            title = str(raw.get("title", "")).strip()
            outcome = str(raw.get("outcome", "")).strip()
            if not title or not outcome:
                continue
            key = str(raw.get("key") or f"g{index}")
            while key in seen_keys:
                key = f"{key}_{index}"
            seen_keys.add(key)
            prerequisites = [
                str(item) for item in raw.get("prerequisite_goal_keys") or [] if str(item) != key
            ]
            goals.append(
                {
                    "key": key,
                    "title": title,
                    "outcome": outcome,
                    "why_it_matters": str(raw.get("why_it_matters", "")).strip(),
                    "prerequisite_goal_keys": prerequisites,
                    "evidence_refs": list(raw.get("evidence_refs") or []),
                }
            )

        if not goals:
            raise HarnessError("HARNESS_NO_GOALS", "The model did not return any usable Goal")

        warnings = quality_gate(goals, depth)
        _low, high = DEPTH_TARGETS.get(depth, DEPTH_TARGETS["standard"])
        if len(goals) > high:
            original_count = len(goals)
            goals = goals[:high]
            warnings.append(
                f"Kept the first {high} of {original_count} Goals to respect {depth} mode"
            )
        valid_keys = {goal["key"] for goal in goals}
        for goal in goals:
            goal["prerequisite_goal_keys"] = [
                key for key in goal["prerequisite_goal_keys"] if key in valid_keys
            ]
        return StepResult.success(
            {"goals": goals},
            events=[
                HarnessEvent(
                    "step.completed",
                    {"step": self.name, "goal_count": len(goals), "warnings": len(warnings)},
                )
            ],
            warnings=warnings,
            metrics={"goal_count": len(goals)},
        )
