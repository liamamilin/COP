"""H50 — Enrich Stages.

Runs once per Main Process. Each Stage becomes "Complete X to obtain Y" with
Concept/Operation candidates attached.
"""

import asyncio
from typing import Any

from app.core.errors import HarnessError
from app.harness.context import HarnessContext, HarnessEvent, StepResult
from app.harness.prompts import build_stage_prompt, detail_limit, trim_evidence
from app.harness.schemas import STAGES_SCHEMA

MAX_CONCEPT_CANDIDATES = 12
MAX_OPERATION_CANDIDATES = 8

#: A detail's fields, in the order the contract reads. Only `title` is
#: mandatory; a Stage that needs no command should not be handed a fake one.
DETAIL_FIELDS = ("title", "action", "command", "expected_result", "caution")


def _as_details(value: Any) -> list[dict[str, Any]]:
    if isinstance(value, dict):
        return [value]
    if isinstance(value, list):
        return [item for item in value if isinstance(item, dict)]
    return []


def _text(value: Any) -> str:
    return str(value).strip() if isinstance(value, (str, int, float)) else ""


def normalize_detail(raw: dict[str, Any]) -> dict[str, Any]:
    """Coerce one implementation detail into the canonical shape.

    `label`/`body` are accepted because that is what the mock emitted before the
    contract existed; an older prompt response is still worth salvaging rather
    than discarding for a field-name difference.

    A `title` that is present but blank is a different case from a missing one,
    and the two are treated differently on purpose. Blank means the model tried
    and failed, so the detail is dropped. Missing means it is likely a legacy
    response, so it is salvaged under a fallback name -- otherwise every detail
    in a slightly older response would be discarded for a field-name difference.
    """
    detail: dict[str, Any] = {}
    for field in DETAIL_FIELDS:
        value = _text(raw.get(field))
        if value:
            detail[field] = value
    if "title" not in detail:
        if "title" in raw:
            return {}
        detail["title"] = _text(raw.get("label")) or _text(raw.get("name")) or "Step"
    if "action" not in detail:
        body = _text(raw.get("body")) or _text(raw.get("description"))
        if body:
            detail["action"] = body
    return detail


def normalize_example(raw: Any) -> dict[str, Any] | None:
    """Coerce an example into `{summary, input?, output?, note?}`, or None."""
    if isinstance(raw, str):
        # A response that answers with the example text itself rather than an
        # object is common enough to be worth keeping.
        return {"summary": raw.strip()} if raw.strip() else None
    if not isinstance(raw, dict):
        return None
    example: dict[str, Any] = {}
    for field in ("summary", "input", "output", "note"):
        value = _text(raw.get(field))
        if value:
            example[field] = value
    if "summary" not in example:
        # Some responses carry a bare string under another name. Treat it as the
        # summary rather than losing it, but an example with no text at all
        # stays absent: an empty object would satisfy the schema and tell the
        # reader nothing.
        for alias in ("text", "body", "description", "example"):
            value = _text(raw.get(alias))
            if value:
                example["summary"] = value
                break
    return example or None


def normalize_stage(
    raw: dict[str, Any],
    source: dict[str, Any],
    goal_key: str,
    *,
    detail_density: str = "balanced",
    evidence_density: str = "key_claims",
) -> dict[str, Any]:
    concepts = [
        str(item).strip() for item in raw.get("concept_candidates") or [] if str(item).strip()
    ]
    operations = [
        str(item).strip() for item in raw.get("operation_candidates") or [] if str(item).strip()
    ]
    details = [
        normalize_detail(item) for item in _as_details(raw.get("implementation_detail_candidates"))
    ]
    detail_max = detail_limit(detail_density)["max_details"]
    return {
        "key": source["key"],
        "title": str(raw.get("title") or source["title"]).strip(),
        "local_goal": str(raw.get("local_goal", "")).strip(),
        "why_it_exists": str(raw.get("why_it_exists", "")).strip(),
        "local_outcome": str(raw.get("local_outcome") or source["local_outcome"]).strip(),
        "dependency_notes": [str(item) for item in raw.get("dependency_notes") or []],
        "concept_candidates": list(dict.fromkeys(concepts))[:MAX_CONCEPT_CANDIDATES],
        "operation_candidates": list(dict.fromkeys(operations))[:MAX_OPERATION_CANDIDATES],
        "implementation_details": details[:detail_max],
        "example": normalize_example(raw.get("example_candidate")),
        # Trimmed here rather than only asked for in the prompt. `detail_density`
        # and `evidence_density` are settings the user can change between runs,
        # so the code has to be what enforces the ceiling; a model asked politely
        # to "keep citations focused" still returns fifteen of them.
        "evidence_refs": trim_evidence(list(raw.get("evidence_refs") or []), evidence_density),
        "process_key": source["process_key"],
        "goal_key": goal_key,
    }


class StageEnrichmentStep:
    name = "H50"

    async def execute(self, ctx: HarnessContext, services: Any) -> StepResult:
        processes = ctx.require("process_drafts")
        language = ctx.settings.get("language", "auto")
        detail_density = ctx.settings.get("detail_density", "balanced")
        evidence_density = ctx.settings.get("evidence_density", "key_claims")
        stage_index = {
            stage["key"]: {**stage, "process_key": process["key"]}
            for process in processes
            for stage in process["stages"]
        }

        async def enrich(process: dict[str, Any]) -> list[dict[str, Any]]:
            if services.is_cancelled():
                raise HarnessError("GENERATION_CANCELLED", "Run cancelled before stage enrichment")
            system, user = build_stage_prompt(
                process=process,
                stages=process["stages"],
                language=language,
                detail_density=detail_density,
                evidence_density=evidence_density,
                # Only the ids this run actually read, so a Stage cannot cite a
                # source the Harness never saw and an unresolvable reference is
                # impossible by construction rather than by filtering.
                source_ids=[str(item.get("id")) for item in ctx.source_bundle if item.get("id")],
            )
            payload = await services.complete_structured(
                system_prompt=system, user_prompt=user, schema=STAGES_SCHEMA
            )
            by_key = {str(item.get("key")): item for item in payload.get("stages") or []}
            enriched: list[dict[str, Any]] = []
            for stage in process["stages"]:
                raw = by_key.get(stage["key"], {})
                normalized = normalize_stage(
                    raw,
                    stage_index[stage["key"]],
                    process["goal_key"],
                    detail_density=detail_density,
                    evidence_density=evidence_density,
                )
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
