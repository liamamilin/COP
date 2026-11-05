"""H50 — Enrich Stages.

Runs once per Main Process. Each Stage becomes "Complete X to obtain Y" with
Concept/Operation candidates attached.
"""

from typing import Any

from app.core.errors import HarnessError
from app.harness.batching import bounded_map, chunked
from app.harness.context import HarnessContext, HarnessEvent, StepResult
from app.harness.prompts import build_stage_prompt, detail_limit, trim_evidence
from app.harness.schemas import STAGES_SCHEMA
from app.harness.teaching_context import (
    normalize_teaching_plan,
    teaching_context,
    teaching_plan_status,
)

#: Concurrent per-process enrichment calls. Six processes used to fan out at
#: once, which pushed a slow provider into timeouts under sustained load. Three
#: keeps a 35-Stage run near its previous wall time now that each call carries
#: fewer Stages.
MAX_ENRICH_CONCURRENCY = 3

#: Stages per enrichment call. A whole process of six or seven Stages with
#: full methods, examples and cautions does not fit in one provider response:
#: the answer is cut off at the output limit, which reaches the user as an
#: unexplained invalid-JSON failure. The process context is still passed to
#: every call, so a Stage does not lose the route it belongs to.
MAX_STAGES_PER_ENRICH_CALL = 3

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
    return {
        "key": source["key"],
        "title": str(raw.get("title") or source["title"]).strip(),
        "local_goal": str(raw.get("local_goal", "")).strip(),
        "why_it_exists": str(raw.get("why_it_exists", "")).strip(),
        "local_outcome": str(raw.get("local_outcome") or source["local_outcome"]).strip(),
        "dependency_notes": [str(item) for item in raw.get("dependency_notes") or []],
        "concept_candidates": list(dict.fromkeys(concepts)),
        "operation_candidates": list(dict.fromkeys(operations)),
        # Density is an authoring target, not a lossy serialization rule. Dropping
        # the tail can remove the write, validation, or recovery half of a task.
        "implementation_details": [detail for detail in details if detail],
        "example": normalize_example(raw.get("example_candidate")),
        # Citations may be capped without deleting execution steps. Instruction
        # density above is deliberately lossless; these are separate policies.
        "evidence_refs": trim_evidence(list(raw.get("evidence_refs") or []), evidence_density),
        "process_key": source["process_key"],
        "goal_key": goal_key,
    }


class StageEnrichmentStep:
    name = "H50"

    async def execute(self, ctx: HarnessContext, services: Any) -> StepResult:
        processes = []
        # Validate all frozen plans before starting any enrichment request. Old
        # checkpoints receive absence metadata only, never a synthesized plan.
        for process in ctx.require("process_drafts"):
            plan = normalize_teaching_plan(process.get("teaching_plan"), process["stages"])
            processes.append({
                **process,
                "teaching_plan": plan,
                "teaching_plan_status": teaching_plan_status(plan),
            })
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
            plan = process["teaching_plan"]
            # The full process object is passed each time: splitting the output
            # must not split the route context the Stage is written for.
            context_payload = teaching_context(ctx, process)
            source_ids = [
                str(item.get("id")) for item in ctx.source_bundle if item.get("id")
            ]
            enriched: list[dict[str, Any]] = []
            for batch in chunked(process["stages"], MAX_STAGES_PER_ENRICH_CALL):
                if services.is_cancelled():
                    raise HarnessError(
                        "GENERATION_CANCELLED", "Run cancelled before the next enrichment batch",
                    )
                system, user = build_stage_prompt(
                    process=process,
                    stages=batch,
                    language=language,
                    detail_density=detail_density,
                    evidence_density=evidence_density,
                    # Only the ids this run actually read, so a Stage cannot cite
                    # a source the Harness never saw and an unresolvable reference
                    # is impossible by construction rather than by filtering.
                    source_ids=source_ids,
                    teaching_context=context_payload,
                    # Authored examples/outcomes are context for continuity, not
                    # evidence that the learner has performed the earlier work.
                    prior_stage_context=[
                        {field: stage[field] for field in (
                            "key", "local_goal", "local_outcome", "why_it_exists", "example",
                        )}
                        for stage in enriched
                    ],
                )
                payload = await services.complete_structured(
                    system_prompt=system, user_prompt=user, schema=STAGES_SCHEMA
                )
                response_stages = payload.get("stages") or []
                response_keys = [str(item.get("key")) for item in response_stages]
                if plan is not None and (
                    len(response_keys) != len(batch)
                    or set(response_keys) != {stage["key"] for stage in batch}
                ):
                    raise HarnessError(
                        "HARNESS_TEACHING_PLAN_COVERAGE",
                        "H50 must return each current-batch planned Stage exactly once",
                    )
                by_key = {str(item.get("key")): item for item in response_stages}
                for stage in batch:
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

        grouped = await bounded_map(
            processes, enrich, concurrency=MAX_ENRICH_CONCURRENCY,
        )
        stage_drafts = [stage for group in grouped for stage in group]
        if not stage_drafts:
            raise HarnessError("HARNESS_NO_STAGES", "No Stage could be enriched")

        warnings = [
            f"Stage '{stage['key']}' has no local outcome"
            for stage in stage_drafts
            if not stage["local_outcome"]
        ]
        warnings.extend(
            f"Process '{process['key']}' has no teaching plan (legacy); "
            "instructional coherence is not verified."
            for process in processes
            if process.get("teaching_plan") is None
        )
        target = detail_limit(detail_density)["max_details"]
        warnings.extend(
            f"Stage '{stage['key']}' has {len(stage['implementation_details'])} details, "
            f"above the {detail_density} target of {target}; all were preserved."
            for stage in stage_drafts
            if len(stage["implementation_details"]) > target
        )
        return StepResult.success(
            {"stage_drafts": stage_drafts, "process_drafts": processes},
            events=[
                HarnessEvent(
                    "step.completed",
                    {"step": self.name, "stage_count": len(stage_drafts)},
                )
            ],
            warnings=warnings,
            metrics={"stage_count": len(stage_drafts)},
        )
