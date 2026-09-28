"""H50 — Enrich Stages.

Runs once per Main Process. Each Stage becomes "Complete X to obtain Y" with
Concept/Operation candidates attached.
"""

import asyncio
from typing import Any

from app.core.errors import HarnessError
from app.harness.context import HarnessContext, HarnessEvent, StepResult
from app.harness.prompts import build_stage_prompt
from app.harness.schemas import STAGES_SCHEMA

MAX_CONCEPT_CANDIDATES = 12
MAX_OPERATION_CANDIDATES = 8


def _as_details(value: Any) -> list[dict[str, Any]]:
    if isinstance(value, dict):
        return [value]
    if isinstance(value, list):
        return [item for item in value if isinstance(item, dict)]
    return []


def normalize_stage(raw: dict[str, Any], source: dict[str, Any], goal_key: str) -> dict[str, Any]:
    concepts = [
        str(item).strip() for item in raw.get("concept_candidates") or [] if str(item).strip()
    ]
    operations = [
        str(item).strip() for item in raw.get("operation_candidates") or [] if str(item).strip()
    ]
    example = _as_details(raw.get("example_candidate"))
    return {
        "key": source["key"],
        "title": str(raw.get("title") or source["title"]).strip(),
        "local_goal": str(raw.get("local_goal", "")).strip(),
        "why_it_exists": str(raw.get("why_it_exists", "")).strip(),
        "local_outcome": str(raw.get("local_outcome") or source["local_outcome"]).strip(),
        "dependency_notes": [str(item) for item in raw.get("dependency_notes") or []],
        "concept_candidates": list(dict.fromkeys(concepts))[:MAX_CONCEPT_CANDIDATES],
        "operation_candidates": list(dict.fromkeys(operations))[:MAX_OPERATION_CANDIDATES],
        "implementation_details": _as_details(raw.get("implementation_detail_candidates")),
        "example": example[0] if example else None,
        "evidence_refs": list(raw.get("evidence_refs") or []),
        "process_key": source["process_key"],
        "goal_key": goal_key,
    }


class StageEnrichmentStep:
    name = "H50"

    async def execute(self, ctx: HarnessContext, services: Any) -> StepResult:
        processes = ctx.require("process_drafts")
        language = ctx.settings.get("language", "auto")
        stage_index = {
            stage["key"]: {**stage, "process_key": process["key"]}
            for process in processes
            for stage in process["stages"]
        }

        async def enrich(process: dict[str, Any]) -> list[dict[str, Any]]:
            if services.is_cancelled():
                raise HarnessError("GENERATION_CANCELLED", "Run cancelled before stage enrichment")
            system, user = build_stage_prompt(
                process=process, stages=process["stages"], language=language
            )
            payload = await services.complete_structured(
                system_prompt=system, user_prompt=user, schema=STAGES_SCHEMA
            )
            by_key = {str(item.get("key")): item for item in payload.get("stages") or []}
            enriched: list[dict[str, Any]] = []
            for stage in process["stages"]:
                raw = by_key.get(stage["key"], {})
                normalized = normalize_stage(raw, stage_index[stage["key"]], process["goal_key"])
                if not normalized["local_goal"]:
                    normalized["local_goal"] = normalized["local_outcome"] or (
                        f"Complete {normalized['title'].lower()}"
                    )
                if not normalized["local_outcome"]:
                    normalized["local_outcome"] = normalized["local_goal"]
                enriched.append(normalized)
            return enriched

        grouped = await asyncio.gather(*(enrich(process) for process in processes))
        stage_drafts = [stage for group in grouped for stage in group]
        if not stage_drafts:
            raise HarnessError("HARNESS_NO_STAGES", "No Stage could be enriched")

        warnings = [
            f"Stage '{stage['key']}' has no local outcome"
            for stage in stage_drafts
            if not stage["local_outcome"]
        ]
        return StepResult.success(
            {"stage_drafts": stage_drafts},
            events=[
                HarnessEvent(
                    "step.completed",
                    {"step": self.name, "stage_count": len(stage_drafts)},
                )
            ],
            warnings=warnings,
            metrics={"stage_count": len(stage_drafts)},
        )
