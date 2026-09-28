"""H100 — Critic.

Two passes, merged into one report:

1. Deterministic heuristics in `critic_rules` catch structural smells.
2. The model pass judges what code cannot: vague Goals, hidden main lines,
   unsupported claims.

Structural findings are never dropped by the model pass, because a model that
returns `severity: pass` must not be able to hide a 14-stage process.
"""

from typing import Any

from app.harness.context import HarnessContext, HarnessEvent, StepResult
from app.harness.prompts import build_critic_prompt
from app.harness.schemas import CRITIC_SCHEMA
from app.harness.steps.critic_rules import check_artifact, merged_report


class CriticStep:
    name = "H100"

    async def execute(self, ctx: HarnessContext, services: Any) -> StepResult:
        artifact = ctx.require("artifact")
        language = ctx.settings.get("language", "auto")

        heuristic_issues = check_artifact(artifact)
        model_report: dict[str, Any] | None = None
        try:
            system, user = build_critic_prompt(artifact=artifact, language=language)
            model_report = await services.complete_structured(
                system_prompt=system, user_prompt=user, schema=CRITIC_SCHEMA
            )
        except Exception as exc:  # noqa: BLE001 - critique is advisory, never fatal
            # A critic outage must not discard a valid artifact.
            return StepResult.success(
                {"critic_report": {"severity": "minor", "issues": heuristic_issues}},
                events=[
                    HarnessEvent(
                        "step.completed",
                        {"step": self.name, "severity": "minor", "critic_unavailable": True},
                    )
                ],
                warnings=[f"The quality critic pass failed: {exc}"],
                metrics={"issue_count": len(heuristic_issues), "critic_unavailable": True},
            )

        report = merged_report(heuristic_issues, model_report)
        return StepResult.success(
            {"critic_report": report},
            events=[
                HarnessEvent(
                    "step.completed",
                    {
                        "step": self.name,
                        "severity": report["severity"],
                        "issue_count": len(report["issues"]),
                    },
                )
            ],
            metrics={"severity": report["severity"], "issue_count": len(report["issues"])},
        )
