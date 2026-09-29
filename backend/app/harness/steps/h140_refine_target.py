"""H140 — Targeted Refinement.

Runs only for a run that names a `target`. Where a normal run rebuilds an entire
COP, this proposes changes to exactly one Goal, Main Process, or Stage and hands
back a patch for review. The artifact is never rewritten here.

The step is fenced twice:

- `apply_revisions` (reused from H110) refuses any field the user edited by
  hand, and
- `build_patch` refuses anything outside the target entity.

A proposal that violates either rule is reported as rejected, with a reason the
user can read, rather than silently dropped. Silently dropping it would leave
the user wondering why the model ignored their instruction.
"""

from typing import Any

from app.domain.patches import REFINABLE_ENTITIES, build_patch
from app.harness.context import HarnessContext, HarnessEvent, StepResult
from app.harness.prompts import build_refine_prompt
from app.harness.schemas import REFINABLE_FIELDS, REFINE_SCHEMA
from app.harness.steps.h110_refine import apply_revisions

TARGET_COLLECTIONS = {
    "goal": "goals",
    "process": "main_processes",
    "stage": "stages",
}


def targeted_artifact_view(
    artifact: dict[str, Any], entity_type: str, entity_id: str
) -> dict[str, Any]:
    """Return only the entity H140 may change plus minimal domain context."""
    collection = TARGET_COLLECTIONS[entity_type]
    target = next(
        (item for item in artifact.get(collection) or [] if str(item.get("id")) == entity_id),
        None,
    )
    return {
        "schema_version": artifact.get("schema_version"),
        "domain": artifact.get("domain"),
        "target": {
            "entity_type": entity_type,
            "entity_id": entity_id,
            "entity": target,
        },
    }


class RefineTargetStep:
    """Propose a patch for one entity, scoped by the run's target."""

    name = "H140"

    async def execute(self, ctx: HarnessContext, services: Any) -> StepResult:
        target = ctx.partial_target
        artifact = ctx.require("artifact")
        if not target:
            return StepResult.fatal(
                "HARNESS_TARGET_MISSING",
                "A targeted refinement needs a target entity",
            )

        entity_type = str(target.get("entity_type") or "")
        entity_id = str(target.get("entity_id") or "")
        if entity_type not in REFINABLE_ENTITIES:
            return StepResult.fatal(
                "TARGET_NOT_REFINABLE",
                f"'{entity_type}' cannot be refined. Refinable types are: "
                f"{', '.join(REFINABLE_ENTITIES)}",
            )

        locked_paths = list(ctx.locked_paths or [])
        instruction = str(ctx.input.get("instruction") or "").strip()
        language = ctx.settings.get("language", "auto")

        # Scope the issue list to the target so the model is not handed the whole
        # artifact's problems and asked to fix all of them.
        issues = self._issues_for(ctx, entity_type, entity_id)
        system, user = build_refine_prompt(
            artifact=targeted_artifact_view(artifact, entity_type, entity_id),
            issues=issues,
            locked_paths=locked_paths,
            language=language,
        )
        if instruction:
            user = f"{user}\n\nThe user asked specifically for: {instruction}"

        payload = await services.complete_structured(
            system_prompt=system, user_prompt=user, schema=REFINE_SCHEMA
        )
        revisions = payload.get("revisions") or []

        # H110's fencing is reused rather than reimplemented, so a manual edit
        # and an AI patch obey exactly the same rule.
        _updated, applied, rejected = apply_revisions(artifact, revisions, locked_paths)

        patch = build_patch(
            artifact,
            entity_type,
            entity_id,
            [
                {
                    "field": item.split(".")[-1],
                    "value": self._value_for(revisions, entity_id, item.split(".")[-1]),
                }
                for item in applied
                if item.split(".")[-1] in REFINABLE_FIELDS[entity_type]
            ],
            locked_paths,
        )
        # Anything H110 refused is surfaced too, so the user learns the model
        # tried to touch a field they had locked.
        for item in rejected:
            patch["rejected"].append(
                {"field": item.get("field", ""), "reason": item.get("reason", "")}
            )

        return StepResult.success(
            {"candidate_patch": patch},
            events=[
                HarnessEvent(
                    "step.completed",
                    {
                        "step": self.name,
                        "entity_type": entity_type,
                        "entity_id": entity_id,
                        "changes": len(patch["changes"]),
                        "rejected": len(patch["rejected"]),
                    },
                )
            ],
            metrics={"changes": len(patch["changes"]), "rejected": len(patch["rejected"])},
        )

    def _issues_for(
        self, ctx: HarnessContext, entity_type: str, entity_id: str
    ) -> list[dict[str, Any]]:
        """Critic issues that name this entity, or a synthetic one.

        When the critic found nothing, a refinement still needs something to
        work from, so a single instruction-shaped issue is synthesised. Without
        it the refiner has nothing to anchor on and returns nothing at all.
        """
        report = ctx.critic_report or {}
        scoped = [
            issue
            for issue in (report.get("issues") or [])
            if str(issue.get("entity_ref") or "") == f"{entity_type}.{entity_id}"
        ]
        if scoped:
            return scoped
        return [
            {
                "code": "USER_REQUESTED_REFINEMENT",
                "entity_ref": f"{entity_type}.{entity_id}",
                "explanation": "The user asked for this entity to be improved.",
                "recommended_change": ctx.input.get("instruction") or "",
            }
        ]

    @staticmethod
    def _value_for(revisions: list[dict[str, Any]], entity_id: str, field: str) -> str:
        for revision in revisions:
            if revision.get("entity_key") == entity_id and revision.get("field") == field:
                return str(revision.get("value") or "")
        return ""
