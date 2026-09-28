"""H110 — Refine.

Runs only for `minor` or `major` critic severity. Enforces three rules the model
cannot be trusted with on its own:

- locked (user-authored) paths are never rewritten,
- only whitelisted text fields may change,
- corrections are local, never whole-entity rewrites.
"""

from typing import Any

from app.harness.context import HarnessContext, HarnessEvent, StepResult
from app.harness.prompts import build_refine_prompt
from app.harness.schemas import REFINABLE_FIELDS, REFINE_SCHEMA

COLLECTIONS = {
    "goal": "goals",
    "process": "main_processes",
    "stage": "stages",
    "concept": "concepts",
    "operation": "operations",
    "branch": "branches",
}


def is_locked(locked_paths: list[str], entity_key: str, field: str) -> bool:
    """True when a user edit owns this entity or this specific field.

    Entity IDs already carry their own type prefix (`goal.x`, `stage.x`), so a
    lock is either the whole entity (`goal.x`) or one field of it
    (`goal.x.why_it_matters`). A lock on one field must not block the others.
    """
    field_path = f"{entity_key}.{field}"
    return any(locked in (entity_key, field_path) for locked in locked_paths)


def apply_revisions(
    artifact: dict[str, Any],
    revisions: list[dict[str, Any]],
    locked_paths: list[str],
) -> tuple[dict[str, Any], list[str], list[dict[str, Any]]]:
    """Apply revisions to a copy of the artifact.

    Returns (new_artifact, applied, rejected).
    """
    import copy

    updated = copy.deepcopy(artifact)
    applied: list[str] = []
    rejected: list[dict[str, Any]] = []
    index_cache: dict[str, dict[str, dict[str, Any]]] = {}

    for revision in revisions:
        entity_type = str(revision.get("entity_type", ""))
        entity_key = str(revision.get("entity_key", ""))
        field = str(revision.get("field", ""))
        value = revision.get("value")
        collection = COLLECTIONS.get(entity_type)
        if collection is None or not entity_key or not field:
            rejected.append({**revision, "reason": "unknown entity type or field"})
            continue
        if field not in REFINABLE_FIELDS[entity_type]:
            rejected.append({**revision, "reason": f"'{field}' is not refinable"})
            continue
        if is_locked(locked_paths, entity_key, field):
            rejected.append({**revision, "reason": "path is locked by user edits"})
            continue
        if not isinstance(value, str) or not value.strip():
            rejected.append({**revision, "reason": "replacement value is empty"})
            continue

        if collection not in index_cache:
            index_cache[collection] = {
                str(entity.get("id")): entity for entity in updated.get(collection) or []
            }
        entity = index_cache[collection].get(entity_key)
        if entity is None:
            rejected.append({**revision, "reason": "entity id not found in artifact"})
            continue
        if field == "example" and entity_type == "stage":
            entity["example"] = {"summary": value.strip()}
        else:
            entity[field] = value.strip()
        applied.append(f"{entity_type}.{entity_key}.{field}")

    return updated, applied, rejected


class RefineStep:
    name = "H110"

    async def execute(self, ctx: HarnessContext, services: Any) -> StepResult:
        artifact = ctx.require("artifact")
        report = ctx.require("critic_report")
        severity = str(report.get("severity", "pass"))
        if severity == "pass":
            return StepResult.success(
                {},
                events=[HarnessEvent("step.completed", {"step": self.name, "skipped": True})],
                metrics={"skipped": True},
            )

        issues = report.get("issues") or []
        locked_paths = list(ctx.locked_paths or [])
        language = ctx.settings.get("language", "auto")
        system, user = build_refine_prompt(
            artifact=artifact, issues=issues, locked_paths=locked_paths, language=language
        )
        payload = await services.complete_structured(
            system_prompt=system, user_prompt=user, schema=REFINE_SCHEMA
        )

        updated, applied, rejected = apply_revisions(
            artifact, payload.get("revisions") or [], locked_paths
        )
        warnings = [f"Refiner proposal skipped: {item.get('reason')}" for item in rejected]
        return StepResult.success(
            {"artifact": updated},
            events=[
                HarnessEvent(
                    "step.completed",
                    {
                        "step": self.name,
                        "severity": severity,
                        "applied": len(applied),
                        "rejected": len(rejected),
                    },
                )
            ],
            warnings=warnings,
            metrics={"applied": len(applied), "rejected": len(rejected)},
        )
