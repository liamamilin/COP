"""H80 — Generate Learning Layer.

Mental Model, Minimal Practices, and Expansion Map. These turn a browsable
artifact into a learnable one.
"""

from typing import Any

from app.harness.context import HarnessContext, HarnessEvent, StepResult
from app.harness.prompts import build_learning_layer_prompt
from app.harness.schemas import LEARNING_LAYER_SCHEMA


class LearningLayerStep:
    name = "H80"

    async def execute(self, ctx: HarnessContext, services: Any) -> StepResult:
        scope = ctx.require("scope_result")
        processes = ctx.require("process_drafts")
        practice_mode = ctx.settings.get("practice_mode", "priority")
        language = ctx.settings.get("language", "auto")
        practices_enabled = practice_mode != "off"

        system, user = build_learning_layer_prompt(
            scope=scope,
            processes=processes,
            practices_enabled=practices_enabled,
            language=language,
        )
        payload = await services.complete_structured(
            system_prompt=system, user_prompt=user, schema=LEARNING_LAYER_SCHEMA
        )

        mental_model = {
            "summary": str((payload.get("mental_model") or {}).get("summary", "")).strip(),
            "flow": [str(item) for item in (payload.get("mental_model") or {}).get("flow") or []],
        }

        process_keys = {process["key"] for process in processes}
        practices: list[dict[str, Any]] = []
        seen: set[str] = set()
        for index, raw in enumerate(payload.get("practices") or [], start=1):
            title = str(raw.get("title", "")).strip()
            process_key = str(raw.get("process_key", "")).strip()
            instructions = [
                str(item) for item in raw.get("instructions") or [] if str(item).strip()
            ]
            if not title or process_key not in process_keys or not instructions:
                continue
            key = f"pr_{process_key}"
            while key in seen:
                key = f"{key}_{index}"
            seen.add(key)
            practices.append(
                {
                    "key": key,
                    "title": title,
                    "process_key": process_key,
                    "instructions": instructions,
                    "expected_outcome": str(raw.get("expected_outcome", "")).strip(),
                    "checkpoint_questions": [
                        str(item) for item in raw.get("checkpoint_questions") or []
                    ],
                }
            )

        expansion_map = [
            {
                "title": str(item.get("title", "")).strip(),
                "description": str(item.get("description", "")).strip(),
                "from_goal_key": str(item.get("from_goal_key") or "") or None,
            }
            for item in payload.get("expansion_map") or []
            if str(item.get("title", "")).strip()
        ]

        warnings: list[str] = []
        if not mental_model["summary"]:
            warnings.append("No Mental Model was produced; the artifact is still browsable")
        if practices_enabled and not practices:
            warnings.append("No Minimal Practice was produced for any Main Process")

        return StepResult.success(
            {
                "mental_model": mental_model,
                "practices": practices,
                "expansion_map": expansion_map,
            },
            events=[
                HarnessEvent(
                    "step.completed",
                    {
                        "step": self.name,
                        "practice_count": len(practices),
                        "expansion_count": len(expansion_map),
                    },
                )
            ],
            warnings=warnings,
            metrics={"practice_count": len(practices)},
        )
