"""H120 — Validate and Repair.

Deterministic validation runs first (JSON Schema, then Pydantic, then
referential integrity). Only if the failure is model-caused does a repair prompt
run, and only up to the configured attempt limit.

Exhausting the limit yields a partial result with checkpoints intact. A failed
repair must never discard the work already done, because the run is still
useful to the user at that point.
"""

import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

from app.domain.cop_models import COPArtifact
from app.harness.context import HarnessContext, HarnessEvent, StepResult, StepStatus
from app.harness.prompts import SHARED_SYSTEM_PREAMBLE, encode_payload
from app.harness.schemas import ARTIFACT_REPAIR_SCHEMA

DEFAULT_MAX_REPAIR_ATTEMPTS = 2
SCHEMA_PATH = "schemas/cop-artifact.schema.json"
SCHEMA_CANDIDATES = (SCHEMA_PATH, "../schemas/cop-artifact.schema.json")


def resolve_schema_path(configured: str | None = None) -> Path | None:
    """Locate the canonical schema, tolerating both repo-root and backend cwd."""
    candidates = [configured] if configured else list(SCHEMA_CANDIDATES)
    for candidate in candidates:
        if not candidate:
            continue
        path = Path(candidate)
        if path.exists():
            return path
    return None


def validate(data: dict[str, Any], schema_path: Path | None = None) -> list[str]:
    """Return human-readable validation errors. Empty list means valid."""
    errors: list[str] = []
    if schema_path is not None:
        with schema_path.open(encoding="utf-8") as handle:
            validator = Draft202012Validator(json.load(handle))
        for error in sorted(validator.iter_errors(data), key=lambda item: list(item.path)):
            location = "/".join(str(part) for part in error.path) or "(root)"
            errors.append(f"{location}: {error.message}")
    if errors:
        return errors
    try:
        COPArtifact.model_validate(data)
    except Exception as exc:  # noqa: BLE001 - rendered as repairable text
        errors.append(str(exc))
    return errors


def build_repair_prompt(
    *, artifact: dict[str, Any], errors: list[str], language: str
) -> tuple[str, str]:
    system = f"""{SHARED_SYSTEM_PREAMBLE}
Task: repair a structurally invalid COP artifact.

The artifact below failed deterministic validation. Fix only the reported
problems. Do not restyle, expand, or rewrite content that already validates.
Preserve every entity ID and every reference that is not itself broken.

Return the complete corrected artifact as one JSON object. Respond in {language}.
"""
    user = f"""Validation errors:
{json.dumps(errors, ensure_ascii=False, indent=2)}

Artifact to repair:
{json.dumps(artifact, ensure_ascii=False, indent=2)}

{encode_payload({"artifact": artifact, "errors": errors})}"""
    return system, user


class ValidateRepairStep:
    name = "H120"

    async def execute(self, ctx: HarnessContext, services: Any) -> StepResult:
        artifact = ctx.require("artifact")
        schema_path = resolve_schema_path(ctx.settings.get("schema_path"))
        max_attempts = int(ctx.settings.get("max_repair_attempts", DEFAULT_MAX_REPAIR_ATTEMPTS))
        language = ctx.settings.get("language", "auto")

        current = artifact
        errors = validate(current, schema_path)
        attempts: list[dict[str, Any]] = []

        for attempt in range(1, max(1, max_attempts) + 1):
            if not errors:
                break
            if services.is_cancelled():
                return StepResult.fatal("GENERATION_CANCELLED", "Run cancelled during repair")
            system, user = build_repair_prompt(artifact=current, errors=errors, language=language)
            try:
                candidate = await services.complete_structured(
                    system_prompt=system, user_prompt=user, schema=ARTIFACT_REPAIR_SCHEMA
                )
            except Exception as exc:  # noqa: BLE001 - provider failure is reportable
                attempts.append({"attempt": attempt, "error": f"repair call failed: {exc}"})
                break
            candidate_errors = validate(candidate, schema_path)
            attempts.append(
                {
                    "attempt": attempt,
                    "errors_before": len(errors),
                    "errors_after": len(candidate_errors),
                }
            )
            # Only accept a repair that strictly reduces the error count;
            # otherwise the model is oscillating and the artifact is not improving.
            if len(candidate_errors) < len(errors):
                current, errors = candidate, candidate_errors
            else:
                break

        if not errors:
            return StepResult.success(
                {"artifact": current},
                events=[
                    HarnessEvent(
                        "step.completed",
                        {"step": self.name, "valid": True, "repair_attempts": len(attempts)},
                    )
                ],
                metrics={"repair_attempts": len(attempts), "valid": True},
            )

        return StepResult(
            status=StepStatus.PARTIAL_SUCCESS,
            events=[
                HarnessEvent(
                    "step.completed",
                    {"step": self.name, "valid": False, "error_count": len(errors)},
                )
            ],
            warnings=[
                "The artifact still fails validation after repair attempts. Work was kept "
                "through the last valid checkpoint; retry finalization or inspect the run."
            ],
            metrics={"repair_attempts": len(attempts), "valid": False, "error_count": len(errors)},
        )
