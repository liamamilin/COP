"""Candidate patches: propose a change to one entity, never apply it silently.

The spec (`16-state-machines.md` §5, `23-coding-agent-milestones.md` M6) puts a
patch in its own state machine:

    generating -> ready -> accepted | rejected | expired

Three rules shape this module:

- A patch is a *proposal*. Producing one changes nothing. Only `accept` writes,
  and it writes to the Draft, never to a published version.
- A patch may only touch one entity. Regenerating a whole COP to fix a sentence
  is how unrelated content gets quietly rewritten.
- User-authored fields are off limits. A locked path is not a soft hint; the
  proposal is rejected for that field and the reason is reported, so the user
  learns that the model wanted to overwrite them.
"""

import copy
from typing import Any

from app.core.errors import CopStudioError
from app.domain.drafting import EDITABLE_FIELDS, ENTITY_COLLECTIONS, lock_path

# Only these three entity types are refinable in V1, per the milestone list.
REFINABLE_ENTITIES = ("goal", "process", "stage")

MAX_PROPOSAL_BYTES = 8000


class FieldChange(dict[str, Any]):
    """One proposed field rewrite, with enough context to render a diff."""


def build_patch(
    artifact: dict[str, Any],
    entity_type: str,
    entity_id: str,
    proposals: list[dict[str, Any]],
    locked_paths: list[str],
) -> dict[str, Any]:
    """Turn model proposals into a reviewable patch.

    Returns a dict with `changes` (accepted proposals, each carrying the before
    value so the UI can show a real diff) and `rejected` (proposals that were
    refused, each with a reason). Nothing here mutates the artifact.
    """
    if entity_type not in REFINABLE_ENTITIES:
        raise CopStudioError(
            "TARGET_NOT_REFINABLE",
            f"'{entity_type}' cannot be refined. Refinable types are: "
            f"{', '.join(REFINABLE_ENTITIES)}",
            status_code=422,
        )

    collection_name = ENTITY_COLLECTIONS[entity_type]
    entity = next(
        (
            item
            for item in (artifact.get(collection_name) or [])
            if str(item.get("id")) == entity_id
        ),
        None,
    )
    if entity is None:
        raise CopStudioError(
            "TARGET_NOT_FOUND",
            f"{entity_type} '{entity_id}' is not part of this artifact",
            status_code=404,
        )

    allowed = EDITABLE_FIELDS[entity_type]
    changes: list[FieldChange] = []
    rejected: list[dict[str, Any]] = []
    seen_fields: set[str] = set()

    for proposal in proposals:
        field = str(proposal.get("field") or "")
        value = proposal.get("value")
        reason: str | None = None

        if field not in allowed:
            reason = f"'{field}' is not a refinable field of {entity_type}"
        elif field in seen_fields:
            reason = f"'{field}' was already proposed; the first change wins"
        elif entity_id in locked_paths or lock_path(entity_id, field) in locked_paths:
            reason = "you edited this field by hand, so it is locked"
        elif not isinstance(value, str) or not value.strip():
            reason = "the proposal was empty"
        elif len(value) > MAX_PROPOSAL_BYTES:
            reason = f"the proposal exceeded {MAX_PROPOSAL_BYTES} characters"

        if reason is not None:
            rejected.append({"field": field, "reason": reason, "value": _as_text(value)})
            continue

        before = entity.get(field)
        changes.append(
            FieldChange(
                field=field,
                before=_as_text(before),
                after=value.strip(),
            )
        )
        seen_fields.add(field)

    return {
        "entity_type": entity_type,
        "entity_id": entity_id,
        "entity_title": _as_text(entity.get("title") or entity.get("name") or entity_id),
        "changes": changes,
        "rejected": rejected,
    }


def apply_patch(artifact: dict[str, Any], patch: dict[str, Any]) -> dict[str, Any]:
    """Return a new artifact with the patch applied.

    Re-validates the result. A patch is model output, so it gets exactly the same
    scrutiny as a hand edit; accepting is not a licence to store something
    broken.
    """
    entity_type = str(patch.get("entity_type") or "")
    entity_id = str(patch.get("entity_id") or "")
    collection_name = ENTITY_COLLECTIONS.get(entity_type)
    changes = patch.get("changes") or []
    if collection_name is None or not changes:
        raise CopStudioError("PATCH_EMPTY", "This patch has no changes to apply", status_code=422)

    updated = copy.deepcopy(artifact)
    entity = next(
        (item for item in (updated.get(collection_name) or []) if str(item.get("id")) == entity_id),
        None,
    )
    if entity is None:
        raise CopStudioError(
            "TARGET_NOT_FOUND",
            f"{entity_type} '{entity_id}' is no longer part of this draft",
            status_code=409,
        )

    for change in changes:
        field = str(change.get("field"))
        entity[field] = change.get("after")
    return updated


def patch_is_stale(patch: dict[str, Any], artifact: dict[str, Any]) -> bool:
    """True when the draft moved on since the patch was proposed.

    A before/after preview is only honest if `before` still matches the draft.
    Otherwise accepting would silently discard whatever the user typed in between.
    """
    entity_type = str(patch.get("entity_type") or "")
    entity_id = str(patch.get("entity_id") or "")
    collection_name = ENTITY_COLLECTIONS.get(entity_type)
    if collection_name is None:
        return True
    entity = next(
        (
            item
            for item in (artifact.get(collection_name) or [])
            if str(item.get("id")) == entity_id
        ),
        None,
    )
    if entity is None:
        return True
    for change in patch.get("changes") or []:
        if _as_text(entity.get(str(change.get("field")))) != change.get("before"):
            return True
    return False


def _as_text(value: Any) -> str:
    """Render any field value as text for the diff.

    `example` is an object in the schema, so a diff cannot assume strings.
    """
    if value is None:
        return ""
    if isinstance(value, str):
        return value
    if isinstance(value, dict):
        summary = value.get("summary")
        return summary if isinstance(summary, str) else ""
    return str(value)
