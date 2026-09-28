"""H10 — Resolve Scope.

Produces the bounded Domain statement every later step depends on.
"""

from typing import Any

from app.core.errors import HarnessError
from app.harness.context import HarnessContext, HarnessEvent, StepResult
from app.harness.prompts import build_scope_prompt
from app.harness.schemas import SCOPE_SCHEMA

VAGUE_SCOPE_MARKERS = ("everything about", "all of", "any ", "general overview of")


def quality_gate(scope: dict[str, Any]) -> list[str]:
    """Return non-blocking warnings when the scope reads as unbounded."""
    warnings: list[str] = []
    text = str(scope.get("scope", "")).lower()
    if not scope.get("domain"):
        return ["Scope is missing a domain name"]
    if any(marker in text for marker in VAGUE_SCOPE_MARKERS):
        warnings.append(
            "Scope reads as an unbounded survey; confirm it still supports one operational Goal."
        )
    if not scope.get("target_user"):
        warnings.append("Scope does not name a target user")
    return warnings


class ScopeStep:
    name = "H10"

    async def execute(self, ctx: HarnessContext, services: Any) -> StepResult:
        intake = ctx.require("input")
        system, user = build_scope_prompt(
            topic=intake.get("topic", ""),
            scope_hint=intake.get("scope_hint", ""),
            target_outcomes=intake.get("target_outcomes", []),
            learner_level=intake.get("learner_level", "new"),
            language=intake.get("language", "auto"),
            sources=ctx.source_bundle,
        )
        payload = await services.complete_structured(
            system_prompt=system, user_prompt=user, schema=SCOPE_SCHEMA
        )
        domain = str(payload.get("domain", "")).strip()
        if not domain:
            raise HarnessError("HARNESS_SCOPE_INVALID", "The model did not return a domain name")

        scope = {
            "domain": domain,
            "scope": str(payload.get("scope", "")).strip(),
            "target_user": str(payload.get("target_user", "")).strip(),
            "non_goals": [str(item) for item in payload.get("non_goals") or []],
            "ambiguity_notes": [str(item) for item in payload.get("ambiguity_notes") or []],
        }
        warnings = quality_gate(scope)
        return StepResult.success(
            {"scope_result": scope},
            events=[
                HarnessEvent(
                    "step.completed",
                    {"step": self.name, "domain": domain, "warnings": len(warnings)},
                )
            ],
            warnings=warnings,
            metrics={"domain": domain},
        )
