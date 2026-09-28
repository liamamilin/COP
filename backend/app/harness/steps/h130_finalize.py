"""H130 — Candidate Finalization.

Stores the candidate artifact and closes the run. There is deliberately no
automatic publish: a generated artifact never overwrites user-owned history
without an explicit user action.
"""

from typing import Any

from app.harness.context import HarnessContext, HarnessEvent, StepResult, StepStatus
from app.harness.steps.h120_validate import resolve_schema_path, validate


class FinalizeStep:
    name = "H130"

    async def execute(self, ctx: HarnessContext, services: Any) -> StepResult:
        artifact = ctx.require("artifact")
        errors = validate(artifact, resolve_schema_path(ctx.settings.get("schema_path")))

        summary = {
            "goals": len(artifact.get("goals") or []),
            "main_processes": len(artifact.get("main_processes") or []),
            "stages": len(artifact.get("stages") or []),
            "concepts": len(artifact.get("concepts") or []),
            "operations": len(artifact.get("operations") or []),
            "branches": len(artifact.get("branches") or []),
            "practices": len(artifact.get("practices") or []),
        }

        if errors:
            return StepResult(
                status=StepStatus.PARTIAL_SUCCESS,
                events=[
                    HarnessEvent(
                        "step.completed",
                        {"step": self.name, "valid": False, "error_count": len(errors)},
                    )
                ],
                warnings=[
                    "Useful partial work exists, but the candidate artifact still has invalid "
                    f"references ({len(errors)} problems). Work was kept through the last valid "
                    "checkpoint."
                ],
                metrics={"valid": False, **summary},
            )

        return StepResult.success(
            {},
            events=[
                HarnessEvent(
                    "step.completed",
                    {"step": self.name, "valid": True, **summary},
                )
            ],
            metrics={"valid": True, **summary},
        )
