"""H20 — Build Research Brief.

Compresses sources into the structure-supporting facts later steps need, without
mirroring the source corpus.
"""

from typing import Any

from app.harness.context import HarnessContext, HarnessEvent, StepResult
from app.harness.prompts import build_research_brief_prompt, trim_evidence
from app.harness.schemas import RESEARCH_BRIEF_SCHEMA


class ResearchBriefStep:
    name = "H20"

    async def execute(self, ctx: HarnessContext, services: Any) -> StepResult:
        scope = ctx.require("scope_result")
        language = ctx.settings.get("language", "auto")
        evidence_density = ctx.settings.get("evidence_density", "key_claims")
        system, user = build_research_brief_prompt(
            scope=scope,
            sources=ctx.source_bundle,
            language=language,
            evidence_density=evidence_density,
        )
        payload = await services.complete_structured(
            system_prompt=system, user_prompt=user, schema=RESEARCH_BRIEF_SCHEMA
        )

        brief = {
            "domain_purpose": str(payload.get("domain_purpose", "")).strip(),
            "capability_candidates": [
                str(item) for item in payload.get("capability_candidates") or []
            ],
            "workflow_candidates": [str(item) for item in payload.get("workflow_candidates") or []],
            "structural_terms": [str(item) for item in payload.get("structural_terms") or []],
            "constraints": [str(item) for item in payload.get("constraints") or []],
            "version_specific_facts": [
                str(item) for item in payload.get("version_specific_facts") or []
            ],
            "evidence_index": trim_evidence(
                list(payload.get("evidence_index") or []), evidence_density
            ),
        }
        warnings = []
        if not brief["capability_candidates"]:
            warnings.append(
                "The research brief found no capability candidates; "
                "Goals will rely on the topic alone."
            )
        # A citation to a source the run never saw is unopenable, and an
        # unopenable citation is worse than none: the user is told the claim is
        # sourced when there is nothing to open. Report it rather than shipping.
        known = {str(item.get("id")) for item in ctx.source_bundle if item.get("id")}
        invented = sorted(
            {
                str(ref.get("source_id"))
                for ref in brief["evidence_index"]
                if str(ref.get("source_id") or "") not in known
            }
            - {""}
        )
        if invented:
            brief["evidence_index"] = [
                ref for ref in brief["evidence_index"] if str(ref.get("source_id")) in known
            ]
            warnings.append(
                "Dropped evidence references to sources this run did not read: "
                + ", ".join(invented)
            )
        return StepResult.success(
            {"research_brief": brief},
            events=[
                HarnessEvent(
                    "step.completed",
                    {
                        "step": self.name,
                        "capabilities": len(brief["capability_candidates"]),
                        "sources": len(ctx.source_bundle),
                    },
                )
            ],
            warnings=warnings,
            metrics={"capability_candidates": len(brief["capability_candidates"])},
        )
