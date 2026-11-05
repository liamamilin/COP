"""Conservative, batch-local identity resolution for H60 (no semantic guessing)."""

import warnings as python_warnings
from typing import Any

from app.core.errors import HarnessError


def normalize_key(value: Any, fallback_name: str, index: int) -> str:
    raw = str(value or "").strip() or str(fallback_name or "").strip()
    cleaned = "".join(char if char.isalnum() else "_" for char in raw.lower()).strip("_")
    return cleaned or f"entity_{index}"


def _text(value: Any) -> str:
    return " ".join(str(value or "").split()).casefold()


def merge_payloads(
    payloads: list[dict[str, Any]],
    *,
    warnings: list[str] | None = None,
) -> dict[str, Any]:
    """Retain every local alias and rewrite relations before combining entities.

    A model may reuse an accepted key only with the same name and a compatible
    definition. A matching name alone (or a substring) is not an identity claim.
    Duplicate keys *within* a response are ambiguous and cannot be repaired.
    """
    notices = warnings if warnings is not None else []
    entities: dict[str, list[dict[str, Any]]] = {"concepts": [], "operations": []}
    by_key: dict[str, dict[str, dict[str, Any]]] = {"concepts": {}, "operations": {}}
    bindings: dict[str, dict[str, list[str]]] = {}

    def notice(message: str) -> None:
        if message not in notices:
            notices.append(message)
            if warnings is None:
                python_warnings.warn(message, RuntimeWarning, stacklevel=3)

    for batch_index, payload in enumerate(payloads, start=1):
        # Snapshots contain only previously accepted entities. Local keys always
        # take precedence, so a collision never silently binds to an older row.
        accepted = {kind: dict(index) for kind, index in by_key.items()}
        local: dict[str, dict[str, str]] = {"concepts": {}, "operations": {}}
        names: dict[str, dict[str, set[str]]] = {"concepts": {}, "operations": {}}
        rows: list[tuple[str, dict[str, Any], dict[str, Any]]] = []

        for kind in entities:
            seen: set[str] = set()
            for position, raw in enumerate(payload.get(kind) or [], start=1):
                if not isinstance(raw, dict) or not str(raw.get("name") or "").strip():
                    raise HarnessError(
                        "HARNESS_INVALID_CANONICAL_IDENTITY",
                        f"H60 batch {batch_index}: {kind} row {position} needs a name.",
                    )
                name = str(raw["name"]).strip()
                proposed = normalize_key(raw.get("key"), name, position)
                if proposed in seen:
                    raise HarnessError(
                        "HARNESS_CANONICAL_KEY_COLLISION",
                        f"H60 batch {batch_index}: duplicate {kind} key '{proposed}'. "
                        "Return a unique key for each entity and use it in every reference.",
                    )
                seen.add(proposed)
                existing = accepted[kind].get(proposed)
                definition = str(raw.get("definition") or "").strip()
                compatible = (
                    existing is not None
                    and _text(existing["name"]) == _text(name)
                    and (
                        not existing["definition"]
                        or not definition
                        or _text(existing["definition"]) == _text(definition)
                    )
                )
                if compatible:
                    target = existing
                    incomplete = not target["definition"] or not definition
                    if not target["definition"] and definition:
                        target["definition"] = definition
                    if incomplete:
                        notice(
                            f"H60 reused {kind} key '{proposed}' with an incomplete definition; "
                            "verify identity before publication."
                        )
                else:
                    key, suffix = proposed, 2
                    while key in by_key[kind]:
                        key = f"{proposed}_{suffix}"
                        suffix += 1
                    if existing is not None:
                        notice(
                            f"H60 kept conflicting {kind} key '{proposed}' as '{key}'; "
                            "name or definition differs from the accepted identity."
                        )
                    if any(_text(item["name"]) == _text(name) for item in entities[kind]):
                        notice(
                            f"H60 retained distinct {kind} identities named '{name}'; "
                            "a matching name alone does not establish equivalence."
                        )
                    target = {"key": key, "name": name, "definition": definition}
                    if kind == "concepts":
                        target.update(
                            role=str(raw.get("role") or "").strip(),
                            related_concept_keys=[],
                            key_operation_keys=[],
                        )
                    else:
                        target.update(
                            purpose=str(raw.get("purpose") or "").strip(),
                            acts_on_concept_keys=[],
                            common_failures=[],
                        )
                    entities[kind].append(target)
                    by_key[kind][key] = target
                local[kind][proposed] = target["key"]
                local[kind][str(raw.get("key") or name).strip()] = target["key"]
                names[kind].setdefault(_text(name), set()).add(target["key"])
                rows.append((kind, raw, target))

        def resolve(
            values: Any,
            kind: str,
            owner: str,
            *,
            batch_index=batch_index,
            local=local,
            accepted=accepted,
            names=names,
        ) -> list[str]:
            resolved: list[str] = []
            if not isinstance(values, (list, tuple)):
                raise HarnessError(
                    "HARNESS_INVALID_CANONICAL_REFERENCE",
                    f"H60 batch {batch_index}: {owner} must contain a list of {kind} keys.",
                )
            for value in values:
                if not isinstance(value, str) or not value.strip():
                    raise HarnessError(
                        "HARNESS_INVALID_CANONICAL_REFERENCE",
                        f"H60 batch {batch_index}: {owner} needs non-empty {kind} key strings.",
                    )
                text = str(value).strip()
                key = local[kind].get(text)
                if key is None:
                    key = local[kind].get(normalize_key(text, "", 0))
                if key is None and text in accepted[kind]:
                    key = text
                if key is None:
                    matches = names[kind].get(_text(text), set())
                    if not matches:
                        matches = {
                            item["key"]
                            for item in accepted[kind].values()
                            if _text(item["name"]) == _text(text)
                        }
                    if len(matches) == 1:
                        key = next(iter(matches))
                if key is None:
                    raise HarnessError(
                        "HARNESS_INVALID_CANONICAL_REFERENCE",
                        f"H60 batch {batch_index}: {owner} references unresolved or ambiguous "
                        f"{kind} '{text}'. Return the entity with a unique key or reference "
                        "an accepted registry key; no unrelated fallback will be attached.",
                    )
                if key not in resolved:
                    resolved.append(key)
            return resolved

        # Process all rows, including repeated accepted identities: later batches
        # may add edges, and those edges use that batch's full local alias map.
        for kind, raw, target in rows:
            relations = (
                (("related_concept_keys", "concepts"), ("key_operation_keys", "operations"))
                if kind == "concepts"
                else (("acts_on_concept_keys", "concepts"),)
            )
            for field, ref_kind in relations:
                for key in resolve(raw.get(field) or [], ref_kind, f"{target['key']}.{field}"):
                    if key not in target[field]:
                        target[field].append(key)
            if kind == "operations":
                for failure in raw.get("common_failures") or []:
                    if str(failure) not in target["common_failures"]:
                        target["common_failures"].append(str(failure))

        for stage_key, binding in (payload.get("stage_bindings") or {}).items():
            if not isinstance(binding, dict):
                raise HarnessError(
                    "HARNESS_INVALID_STAGE_BINDING",
                    f"H60 batch {batch_index}: Stage '{stage_key}' needs a binding object.",
                )
            if str(stage_key) in bindings:
                raise HarnessError(
                    "HARNESS_INVALID_STAGE_BINDING",
                    f"H60 Stage '{stage_key}' was bound in more than one batch.",
                )
            bindings[str(stage_key)] = {
                field: resolve(binding.get(field) or [], kind, f"Stage '{stage_key}'.{field}")
                for field, kind in (("concept_keys", "concepts"), ("operation_keys", "operations"))
            }

    return {**entities, "stage_bindings": bindings}
