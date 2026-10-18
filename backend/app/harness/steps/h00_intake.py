"""H00 — Intake.

Deterministic normalization of user input. No LLM call is required, which is
why this step never touches the provider.
"""

from typing import Any

from app.harness.context import HarnessContext, HarnessEvent, StepResult

MAX_SOURCE_EXCERPT = 4000


def normalize_intake(
    *,
    topic: str,
    scope_hint: str,
    target_outcomes: list[str],
    learner_level: str,
    language: str,
    depth: str,
    selected_source_ids: list[str],
    source_bundle: list[dict[str, Any]],
) -> dict[str, Any]:
    """Collapse raw run input and source text into the canonical intake shape."""
    selected = set(selected_source_ids)
    sources = [
        {
            "id": str(item.get("id", "")),
            "title": str(item.get("title", "")),
            "type": str(item.get("type", "")),
            "excerpt": str(item.get("text", ""))[:MAX_SOURCE_EXCERPT],
        }
        for item in source_bundle
        if not selected or str(item.get("id", "")) in selected
    ]
    return {
        "topic": topic.strip(),
        "scope_hint": scope_hint.strip(),
        "target_outcomes": [item.strip() for item in target_outcomes if item.strip()],
        "learner_level": learner_level,
        "language": language,
        "depth": depth,
        "source_ids": [item["id"] for item in sources if item["id"]],
        "sources": sources,
    }


def missing_inputs(ctx: HarnessContext) -> list[str]:
    """Only a completely empty request is fatal.

    Topic-only generation is explicitly supported, and a source without a topic
    is also workable once scope resolution runs, so neither alone is an error.
    """
    if not ctx.input.get("topic", "").strip() and not ctx.input.get("source_ids"):
        return ["topic or source"]
    return []


class IntakeStep:
    name = "H00"

    async def execute(self, ctx: HarnessContext, services: Any) -> StepResult:
        missing = missing_inputs(ctx)
        if missing:
            return StepResult.fatal(
                "HARNESS_INTAKE_INCOMPLETE",
                f"Generation requires {' or '.join(missing)}",
            )

        intake = normalize_intake(
            topic=ctx.input.get("topic", ""),
            scope_hint=ctx.input.get("scope_hint", ""),
            target_outcomes=list(ctx.input.get("target_outcomes") or []),
            # Settings first, request second. It used to read `ctx.input` alone,
            # so a learner level chosen once in Settings was ignored by every
            # run and the only value that worked was the per-request field. The
            # request still wins when it carries one, which keeps an explicit
            # per-run override authoritative.
            learner_level=ctx.input.get("learner_level")
            or ctx.settings.get("learner_level", "new"),
            language=ctx.settings.get("language", "auto"),
            depth=ctx.settings.get("generation_depth", "standard"),
            selected_source_ids=list(ctx.input.get("source_ids") or []),
            source_bundle=ctx.source_bundle,
        )
        return StepResult.success(
            {"intake": intake},
            events=[
                HarnessEvent(
                    "step.completed",
                    {
                        "step": self.name,
                        "topic": intake["topic"],
                        "source_count": len(intake["source_ids"]),
                    },
                )
            ],
            metrics={"source_count": len(intake["source_ids"])},
        )
