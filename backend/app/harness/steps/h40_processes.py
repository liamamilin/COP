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

MIN_STAGES = 3
MAX_STAGES = 8
STAGE_LIMIT_WARNING = 10


def normalize_process(raw: dict[str, Any], goal: dict[str, Any]) -> dict[str, Any]:
    """Keep the stage count inside the documented range and rekey stages."""
    raw_stages = [item for item in raw.get("stages") or [] if str(item.get("title", "")).strip()]
    trimmed = raw_stages[:MAX_STAGES]
    stages: list[dict[str, Any]] = []
    for index, stage in enumerate(trimmed, start=1):
        title = str(stage["title"]).strip()
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
    return {
        "key": f"p_{goal['key']}",
        "goal_key": goal["key"],
        "title": str(raw.get("title") or goal["title"]).strip(),
        "outcome": str(raw.get("outcome") or goal["outcome"]).strip(),
        "stage_keys": [stage["key"] for stage in stages],
        "stages": stages,
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

        async def build(goal: dict[str, Any]) -> dict[str, Any]:
            if services.is_cancelled():
                raise HarnessError("GENERATION_CANCELLED", "Run cancelled before process build")
            system, user = build_process_prompt(
                goal=goal,
                scope=scope,
                brief=brief,
                siblings=[other for other in goals if other["key"] != goal["key"]],
                language=language,
            )
            payload = await services.complete_structured(
                system_prompt=system, user_prompt=user, schema=PROCESSES_SCHEMA
            )
            return normalize_process(payload, goal)

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
