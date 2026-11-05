"""Bounded instructional context for H50; no I/O or new model calls.

Read only frozen run inputs/checkpoints. A prerequisite's planned outcome is
context, never evidence that the learner has already completed that work.
"""

from copy import deepcopy
from typing import Any

from jsonschema import Draft202012Validator

from app.core.errors import HarnessError
from app.harness.context import HarnessContext
from app.harness.schemas import TEACHING_PLAN_SCHEMA


def normalize_teaching_plan(
    plan: Any,
    stages: list[dict[str, Any]],
    *,
    stage_key_map: dict[str, str] | None = None,
) -> dict[str, Any] | None:
    """Validate/rekey a plan without inventing missing instructional content.

    None is the explicit legacy path. A supplied but invalid plan must not be
    downgraded to legacy, including references to stages lost in normalization.
    This proves reference integrity only, not instructional effectiveness.
    """
    if plan is None:
        return None
    error = next(Draft202012Validator(TEACHING_PLAN_SCHEMA).iter_errors(plan), None)
    if error is not None:
        raise HarnessError("HARNESS_TEACHING_PLAN_INVALID", error.message)
    normalized = deepcopy(plan)
    keys = [stage["key"] for stage in stages]
    mapping = stage_key_map if stage_key_map is not None else {key: key for key in keys}

    def resolve(key: str) -> str:
        if key not in mapping or mapping[key] not in keys:
            raise HarnessError(
                "HARNESS_TEACHING_PLAN_REFERENCE",
                f"Teaching plan references unresolved Stage '{key}'",
            )
        return mapping[key]

    for entry in normalized["stages"]:
        entry["stage_key"] = resolve(entry["stage_key"])
        entry["builds_on"] = [resolve(key) for key in entry["builds_on"]]
    if [entry["stage_key"] for entry in normalized["stages"]] != keys:
        raise HarnessError(
            "HARNESS_TEACHING_PLAN_COVERAGE",
            "Teaching plan must cover every process Stage exactly once in route order",
        )
    earlier: set[str] = set()
    for entry in normalized["stages"]:
        if any(key not in earlier for key in entry["builds_on"]):
            raise HarnessError(
                "HARNESS_TEACHING_PLAN_FORWARD_REFERENCE",
                f"Stage '{entry['stage_key']}' may build only on earlier Stages",
            )
        earlier.add(entry["stage_key"])
    return normalized


def teaching_plan_status(plan: dict[str, Any] | None) -> str:
    return "present_unverified" if plan is not None else "legacy_absent_unverified"


def teaching_context(ctx: HarnessContext, process: dict[str, Any]) -> dict[str, Any]:
    goals = {goal["key"]: goal for goal in ctx.goals}
    goal = goals.get(process["goal_key"], {})
    prerequisites = [
        {"key": key, "title": goals[key]["title"], "planned_outcome": goals[key]["outcome"]}
        for key in goal.get("prerequisite_goal_keys") or []
        if key in goals
    ]
    excerpts = []
    for source in ctx.source_bundle[:4]:
        text = str(source.get("excerpt") or "")
        excerpts.append({
            "id": source.get("id"),
            "title": source.get("title"),
            "excerpt": text[:1800],
            "excerpt_truncated": len(text) > 1800,
        })
    return {
        "scope": ctx.scope_result or {},
        "learner_level": ctx.settings.get("learner_level")
        or ctx.input.get("learner_level", "new"),
        "goal": goal,
        "teaching_plan": process.get("teaching_plan"),
        "teaching_plan_status": teaching_plan_status(process.get("teaching_plan")),
        "prerequisite_planned_outputs": prerequisites,
        "source_material": excerpts,
        "sources_omitted": max(0, len(ctx.source_bundle) - len(excerpts)),
        "research_constraints": (ctx.research_brief or {}).get("constraints", []),
        "version_specific_facts": (ctx.research_brief or {}).get("version_specific_facts", []),
    }
