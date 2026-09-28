"""H60 — Canonicalize Concepts and Operations.

Runs once across all processes because it merges synonyms globally. It must not
be parallelized per process: cross-process merging is the entire point.
"""

from typing import Any

from app.core.errors import HarnessError
from app.harness.context import HarnessContext, HarnessEvent, StepResult
from app.harness.prompts import build_canonicalize_prompt
from app.harness.schemas import CANONICALIZE_SCHEMA

STAGE_KEYS_ATTRIBUTE = "stage_keys"


def _normalize_key(value: Any, fallback_name: str, index: int) -> str:
    """Normalize a model-supplied key into a stable snake_case identifier.

    A key the model already provides is trusted and only sanitized, so the same
    key can round-trip from `concepts[].key` into `stage_bindings`. Appending an
    index unconditionally would break that correspondence, because the binding
    references the key the model wrote, not a renumbered one.
    """
    raw = str(value or "").strip() or str(fallback_name or "").strip()
    cleaned = "".join(char if char.isalnum() else "_" for char in raw.lower()).strip("_")
    return cleaned or f"entity_{index}"


def canonicalize(payload: dict[str, Any]) -> dict[str, Any]:
    """Merge synonyms and produce stable keys plus Stage bindings."""
    concepts: list[dict[str, Any]] = []
    concept_index: dict[str, int] = {}
    for index, raw in enumerate(payload.get("concepts") or [], start=1):
        name = str(raw.get("name", "")).strip()
        if not name:
            continue
        dedupe_key = name.lower()
        if dedupe_key in concept_index:
            existing = concepts[concept_index[dedupe_key]]
            if not existing["definition"] and raw.get("definition"):
                existing["definition"] = str(raw["definition"]).strip()
            continue
        concept_index[dedupe_key] = len(concepts)
        concepts.append(
            {
                "key": _normalize_key(raw.get("key"), name, index),
                "name": name,
                "definition": str(raw.get("definition", "")).strip(),
                "role": str(raw.get("role", "")).strip(),
                "related_concept_keys": [
                    str(item) for item in raw.get("related_concept_keys") or []
                ],
                "key_operation_keys": [str(item) for item in raw.get("key_operation_keys") or []],
            }
        )

    operations: list[dict[str, Any]] = []
    operation_index: dict[str, int] = {}
    for index, raw in enumerate(payload.get("operations") or [], start=1):
        name = str(raw.get("name", "")).strip()
        if not name:
            continue
        dedupe_key = name.lower()
        if dedupe_key in operation_index:
            continue
        operation_index[dedupe_key] = len(operations)
        operations.append(
            {
                "key": _normalize_key(raw.get("key"), name, index),
                "name": name,
                "definition": str(raw.get("definition", "")).strip(),
                "purpose": str(raw.get("purpose", "")).strip(),
                "acts_on_concept_keys": [
                    str(item) for item in raw.get("acts_on_concept_keys") or []
                ],
                "common_failures": [str(item) for item in raw.get("common_failures") or []],
            }
        )

    concept_keys = {concept["key"] for concept in concepts}
    concept_names = {concept["name"].lower(): concept["key"] for concept in concepts}
    operation_keys = {operation["key"] for operation in operations}
    operation_names = {operation["name"].lower(): operation["key"] for operation in operations}

    for concept in concepts:
        concept["related_concept_keys"] = [
            key for key in concept["related_concept_keys"] if key in concept_keys
        ]
        concept["key_operation_keys"] = [
            key for key in concept["key_operation_keys"] if key in operation_keys
        ]
    for operation in operations:
        resolved: list[str] = []
        for ref in operation["acts_on_concept_keys"]:
            key = ref if ref in concept_keys else concept_names.get(ref.lower())
            if key and key not in resolved:
                resolved.append(key)
        operation["acts_on_concept_keys"] = resolved

    def resolve(values: Any, names: dict[str, str], valid: set[str]) -> list[str]:
        """Accept a reference written either as a key or as a display name."""
        resolved: list[str] = []
        for value in values or []:
            text = str(value)
            key = text if text in valid else names.get(text.lower())
            if key and key not in resolved:
                resolved.append(key)
        return resolved

    bindings: dict[str, dict[str, list[str]]] = {}
    for stage_key, binding in (payload.get("stage_bindings") or {}).items():
        bindings[str(stage_key)] = {
            "concept_keys": resolve(
                (binding or {}).get("concept_keys"), concept_names, concept_keys
            ),
            "operation_keys": resolve(
                (binding or {}).get("operation_keys"), operation_names, operation_keys
            ),
        }

    return {"concepts": concepts, "operations": operations, "stage_bindings": bindings}


class CanonicalizeStep:
    name = "H60"

    async def execute(self, ctx: HarnessContext, services: Any) -> StepResult:
        stage_drafts = ctx.require("stage_drafts")
        language = ctx.settings.get("language", "auto")
        system, user = build_canonicalize_prompt(stages=stage_drafts, language=language)
        payload = await services.complete_structured(
            system_prompt=system, user_prompt=user, schema=CANONICALIZE_SCHEMA
        )
        result = canonicalize(payload)

        if not result["concepts"] or not result["operations"]:
            raise HarnessError(
                "HARNESS_NO_CANONICAL_CORE",
                "The model returned no Concepts or no Operations",
            )

        # Stages whose binding is missing still need one Concept and Operation
        # so the artifact never renders an empty Stage.
        stage_keys = [stage["key"] for stage in stage_drafts]
        warnings: list[str] = []
        for stage in stage_drafts:
            key = stage["key"]
            binding = result["stage_bindings"].setdefault(
                key, {"concept_keys": [], "operation_keys": []}
            )
            if not binding["concept_keys"]:
                binding["concept_keys"] = [result["concepts"][0]["key"]]
                warnings.append(
                    f"Stage '{key}' had no Concept binding; attached the primary Concept"
                )
            if not binding["operation_keys"]:
                binding["operation_keys"] = [result["operations"][0]["key"]]
                warnings.append(
                    f"Stage '{key}' had no Operation binding; attached the primary Operation"
                )

        return StepResult.success(
            {
                "concepts": result["concepts"],
                "operations": result["operations"],
                "stage_bindings": result["stage_bindings"],
                "bound_stage_keys": stage_keys,
            },
            events=[
                HarnessEvent(
                    "step.completed",
                    {
                        "step": self.name,
                        "concept_count": len(result["concepts"]),
                        "operation_count": len(result["operations"]),
                    },
                )
            ],
            warnings=warnings,
            metrics={
                "concept_count": len(result["concepts"]),
                "operation_count": len(result["operations"]),
            },
        )
