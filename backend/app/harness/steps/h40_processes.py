"""H40 — Build Main Processes.

Runs once per Goal. Safe to parallelize once the shared context (scope, brief,
goals) is stable.
"""

import asyncio
from typing import Any

from app.core.errors import HarnessError
from app.harness.context import HarnessContext, HarnessEvent, StepResult
from app.harness.prompts import build_process_prompt
from app.harness.schemas import PROCESSES_SCHEMA
from app.harness.teaching_context import normalize_teaching_plan, teaching_plan_status

MIN_STAGES = 3
MAX_STAGES = 8
STAGE_LIMIT_WARNING = 10
DEPTH_STAGE_LIMITS = {"fast": 5, "standard": 8, "deep": 8}


def normalize_process(
    raw: dict[str, Any], goal: dict[str, Any], *, max_stages: int = MAX_STAGES
) -> dict[str, Any]:
    """Rekey the route and its plan together; retain legacy no-plan responses."""
    raw_stages = [item for item in raw.get("stages") or [] if str(item.get("title", "")).strip()]
    has_plan = raw.get("teaching_plan") is not None
    if has_plan and len(raw_stages) > max_stages:
        raise HarnessError(
            "HARNESS_TEACHING_PLAN_TRUNCATED",
            f"Process for Goal '{goal['key']}' exceeds {max_stages} Stages; "
            "cannot silently truncate a planned route",
        )
    trimmed = raw_stages[:max_stages]
    stages: list[dict[str, Any]] = []
    stage_key_map: dict[str, str] = {}
    for index, stage in enumerate(trimmed, start=1):
        title = str(stage["title"]).strip()
        original_key = str(stage.get("key") or "").strip()
        if has_plan and (not original_key or original_key in stage_key_map):
            raise HarnessError(
                "HARNESS_TEACHING_PLAN_REFERENCE", "Planned Stages need unique non-empty keys"
            )
        stage_key_map[original_key] = f"{goal['key']}_s{index}"
        stages.append(
            {
                "key": f"{goal['key']}_s{index}",
                "title": title,
                "normalized_title": title.lower(),
                "local_outcome": str(stage.get("local_outcome", "")).strip(),
            }
        )
    if not stages:
        raise HarnessError(
            "HARNESS_PROCESS_EMPTY", f"Process for Goal '{goal['key']}' has no Stage"
        )
    plan = normalize_teaching_plan(raw.get("teaching_plan"), stages, stage_key_map=stage_key_map)
    return {
        "key": f"p_{goal['key']}",
        "goal_key": goal["key"],
        "title": str(raw.get("title") or goal["title"]).strip(),
        "outcome": str(raw.get("outcome") or goal["outcome"]).strip(),
        "stage_keys": [stage["key"] for stage in stages],
        "stages": stages,
        "teaching_plan": plan,
        "teaching_plan_status": teaching_plan_status(plan),
    }


class ProcessBuildStep:
    name = "H40"

    async def execute(self, ctx: HarnessContext, services: Any) -> StepResult:
        goals = ctx.require("goals")
        if not goals:
            raise HarnessError("HARNESS_NO_GOALS", "No Goal is available to build a process for")
        scope = ctx.require("scope_result")
        brief = ctx.require("research_brief")
        language = ctx.settings.get("language", "auto")
        depth = ctx.settings.get("generation_depth", "standard")
        max_stages = DEPTH_STAGE_LIMITS.get(depth, MAX_STAGES)

        async def build(goal: dict[str, Any]) -> dict[str, Any]:
            if services.is_cancelled():
                raise HarnessError("GENERATION_CANCELLED", "Run cancelled before process build")
            system, user = build_process_prompt(
                goal=goal,
                scope=scope,
                brief=brief,
                siblings=[other for other in goals if other["key"] != goal["key"]],
                language=language,
                max_stages=max_stages,
                learner_level=ctx.settings.get("learner_level")
                or ctx.input.get("learner_level", "new"),
            )
            payload = await services.complete_structured(
                system_prompt=system, user_prompt=user, schema=PROCESSES_SCHEMA
            )
            return normalize_process(payload, goal, max_stages=max_stages)

        results = await asyncio.gather(*(build(goal) for goal in goals))
        processes = [process for process in results if process]
        if not processes:
            raise HarnessError(
                "HARNESS_NO_PROCESSES", "No Main Process could be constructed for any Goal"
            )

        warnings: list[str] = []
        for process in processes:
            count = len(process["stage_keys"])
            title = process["title"]
            if process["teaching_plan"] is None:
                warnings.append(
                    f"Process '{title}' has no teaching plan (legacy); "
                    "instructional coherence is not verified."
                )
            if count < MIN_STAGES:
                warnings.append(
                    f"Process '{title}' has {count} stages; 3-8 keeps the main line readable"
                )
            elif count > STAGE_LIMIT_WARNING:
                warnings.append(
                    f"Process '{title}' has {count} stages and may no longer be scannable"
                )

        return StepResult.success(
            {"process_drafts": processes},
            events=[
                HarnessEvent(
                    "step.completed",
                    {
                        "step": self.name,
                        "process_count": len(processes),
                        "stage_count": sum(len(p["stage_keys"]) for p in processes),
                    },
                )
            ],
            warnings=warnings,
            metrics={
                "process_count": len(processes),
                "stage_count": sum(len(p["stage_keys"]) for p in processes),
            },
        )
