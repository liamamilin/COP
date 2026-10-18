"""Draft editing: candidate → draft, manual field edits, publish.

Three invariants from the spec (`16-state-machines.md` §4, `24-cross-layer-consistency.md`
§9) drive this module:

- `COPVersion` is immutable. There is no code path here that updates one.
- A project has at most one active draft, enforced by a unique index rather
  than by a read-then-write check, so two concurrent requests cannot both win.
- Publishing is an explicit user action. Nothing in the Harness calls
  `publish_draft`.

Every write re-validates the whole artifact. A draft that references a
deleted concept is not a draft, it is a broken document, and letting it persist
would push the failure to the moment of publishing, where the user has the least
context about what went wrong.
"""

import copy
import uuid
from typing import Any

from app.core.errors import CopStudioError, NotFoundError
from app.domain.validation import validate_artifact

# Editable text fields per entity type, mirroring the canonical artifact shape.
# `id` and every `*_ref` / `*_refs` field are deliberately absent: references are
# structure, and structure is the code's job (same split as Shared Foundation
# detection in H70). Letting a PATCH body rewrite `stage_refs` would let a
# client silently drop a Stage from the main line.
EDITABLE_FIELDS: dict[str, frozenset[str]] = {
    "goal": frozenset({"title", "outcome", "why_it_matters"}),
    "process": frozenset({"title", "outcome"}),
    # `implementation_details` and `common_failures` are here because the content
    # gate reports them by name. A gate that blocks publication on a field the
    # user cannot reach is a dead end rather than a quality check.
    "stage": frozenset(
        {
            "title",
            "local_goal",
            "why_it_exists",
            "local_outcome",
            "example",
            "implementation_details",
        }
    ),
    "concept": frozenset({"name", "definition", "role"}),
    "operation": frozenset({"name", "definition", "purpose", "common_failures"}),
}

#: Fields edited as one `|`-separated line per entry rather than as nested
#: inputs. A form of nested repeatable inputs is a rich text editor by another
#: name, and spec `19` excludes one from V1.
LINE_EDITED_FIELDS: dict[str, frozenset[str]] = {
    "stage": frozenset({"implementation_details"}),
    "operation": frozenset({"common_failures"}),
}

DETAIL_FIELDS = ("title", "action", "command", "expected_result", "caution")
DETAIL_SEPARATOR = "|"


def parse_detail_lines(text: str) -> list[dict[str, str]]:
    """Parse `title | action | command | expected result | caution` lines.

    The separator is `|` rather than a comma or a newline because a shell command
    and an expected result both contain commas, and a pasted multi-line command
    would otherwise silently become several details. A line with no separator is
    still accepted as a bare title, so a user adding a first line is not forced
    to learn the format before they can make progress.
    """
    details: list[dict[str, str]] = []
    for line in text.splitlines():
        entry = line.strip()
        if not entry:
            continue
        parts = [part.strip() for part in entry.split(DETAIL_SEPARATOR)]
        detail: dict[str, str] = {}
        for index, field in enumerate(DETAIL_FIELDS):
            if index < len(parts) and parts[index]:
                detail[field] = parts[index]
        if not detail.get("title") and len(parts) == 1 and parts[0]:
            detail["title"] = parts[0]
        if detail.get("title"):
            details.append(detail)
    return details


def parse_string_lines(text: str) -> list[str]:
    """Parse a newline-separated list, dropping blank lines."""
    return [line.strip() for line in text.splitlines() if line.strip()]


# API path segment -> artifact collection. API paths are plural nouns
# (`/goals`, `/processes`, ...) while the domain types are singular, and
# `/processes` is the API name for the `MainProcess` domain entity (spec 24 §4).
ENTITY_COLLECTIONS: dict[str, str] = {
    "goal": "goals",
    "process": "main_processes",
    "stage": "stages",
    "concept": "concepts",
    "operation": "operations",
}

# Plural API path segment -> singular domain entity type.
PATH_ENTITIES: dict[str, str] = {
    "goals": "goal",
    "processes": "process",
    "stages": "stage",
    "concepts": "concept",
    "operations": "operation",
}


def resolve_entity_type(segment: str) -> str | None:
    """Map an API path segment to a domain entity type, or None if unknown."""
    return PATH_ENTITIES.get(segment)


def lock_path(entity_id: str, field: str) -> str:
    """The lock token for one field, matching the H110 refiner's format.

    Entity ids already carry their own type prefix (`goal.x`), so a lock is
    either a whole entity (`goal.x`) or one field of it (`goal.x.outcome`).
    Using the same string format in both places is what lets a draft's locks be
    handed straight to the Harness without translation.
    """
    return f"{entity_id}.{field}"


def with_locks(locked: list[str] | None, entity_id: str, changed_fields: list[str]) -> list[str]:
    """Return the lock list extended with the fields just edited.

    Only fields whose value actually changed are locked. Resaving a form
    unchanged must not quietly make content un-refinable forever, so callers
    pass the diff, not the whole form.
    """
    updated = list(locked or [])
    for field in changed_fields:
        token = lock_path(entity_id, field)
        if token not in updated:
            updated.append(token)
    return updated


MAX_FIELD_LENGTH = 8000
MAX_ENTITY_ID_LENGTH = 180


def _validate(data: dict[str, Any], schema_path: Any) -> None:
    try:
        validate_artifact(data, schema_path)
    except Exception as exc:  # noqa: BLE001 - jsonschema and pydantic raise different types
        raise CopStudioError(
            "DRAFT_VALIDATION_FAILED",
            f"This edit would leave the draft invalid, so it was rejected: {exc}",
            status_code=422,
            details={"reason": str(exc)},
        ) from exc


def apply_entity_edit(
    artifact: dict[str, Any],
    entity_type: str,
    entity_id: str,
    changes: dict[str, Any],
    *,
    schema_path: Any,
) -> dict[str, Any]:
    """Return a new artifact with one entity's editable text fields replaced.

    Raises rather than persisting a partial edit: an invalid draft is worse than
    a rejected request, because the user cannot tell how far the damage goes.

    Returns the new artifact and the fields whose value actually changed. The
    caller needs that second value to record locks: a PATCH that resends an
    unchanged field must not make it permanently un-refinable.
    """
    allowed = EDITABLE_FIELDS.get(entity_type)
    collection_name = ENTITY_COLLECTIONS.get(entity_type)
    if allowed is None or collection_name is None:
        raise CopStudioError(
            "UNKNOWN_ENTITY_TYPE",
            f"'{entity_type}' is not an editable entity type",
            status_code=404,
        )
    if not changes:
        raise CopStudioError("EMPTY_EDIT", "Provide at least one field to change", status_code=422)

    unknown = sorted(set(changes) - allowed)
    if unknown:
        raise CopStudioError(
            "FIELD_NOT_EDITABLE",
            f"These fields cannot be edited by hand: {', '.join(unknown)}. "
            f"Editable fields are: {', '.join(sorted(allowed))}",
            status_code=422,
            details={"rejected": unknown, "editable": sorted(allowed)},
        )

    updated = copy.deepcopy(artifact)
    entities = updated.get(collection_name) or []
    target = next((item for item in entities if str(item.get("id")) == entity_id), None)
    if target is None:
        raise NotFoundError(
            f"{entity_type} '{entity_id}' is not part of this draft",
            code="ENTITY_NOT_FOUND",
        )

    changed: list[str] = []
    for field, value in changes.items():
        before = copy.deepcopy(target.get(field))
        if field == "example":
            # The schema types `example` as an object or null. Accept a bare
            # string for convenience and keep the shape the renderer expects.
            target["example"] = None if value in (None, "") else {"summary": str(value).strip()}
            if target.get(field) != before:
                changed.append(field)
            continue
        if field in LINE_EDITED_FIELDS.get(entity_type, frozenset()):
            if not isinstance(value, str):
                raise CopStudioError(
                    "FIELD_TYPE_INVALID",
                    f"'{field}' must be a string, one entry per line",
                    status_code=422,
                    details={"field": field},
                )
            stripped = value.strip()
            if len(stripped) > MAX_FIELD_LENGTH:
                raise CopStudioError(
                    "FIELD_TOO_LONG",
                    f"'{field}' exceeds {MAX_FIELD_LENGTH} characters",
                    status_code=422,
                    details={"field": field},
                )
            target[field] = (
                parse_detail_lines(stripped)
                if field == "implementation_details"
                else parse_string_lines(stripped)
            )
            if target[field] != before:
                changed.append(field)
            continue
        if not isinstance(value, str):
            raise CopStudioError(
                "FIELD_TYPE_INVALID",
                f"'{field}' must be a string",
                status_code=422,
                details={"field": field},
            )
        stripped = value.strip()
        if len(stripped) > MAX_FIELD_LENGTH:
            raise CopStudioError(
                "FIELD_TOO_LONG",
                f"'{field}' exceeds {MAX_FIELD_LENGTH} characters",
                status_code=422,
                details={"field": field},
            )
        # Required text fields must not be emptied: an empty `title` produces a
        # schema-invalid artifact, and a blank outcome is not reviewable.
        if field in _REQUIRED_TEXT.get(entity_type, frozenset()) and not stripped:
            raise CopStudioError(
                "FIELD_REQUIRED",
                f"'{field}' cannot be empty",
                status_code=422,
                details={"field": field},
            )
        target[field] = stripped
        if target[field] != before:
            changed.append(field)

    _validate(updated, schema_path)
    return updated, changed


_REQUIRED_TEXT: dict[str, frozenset[str]] = {
    "goal": frozenset({"title", "outcome"}),
    "process": frozenset({"title", "outcome"}),
    "stage": frozenset({"title", "local_goal"}),
    "concept": frozenset({"name", "definition", "role"}),
    "operation": frozenset({"name", "definition"}),
}


def apply_metadata_edit(
    artifact: dict[str, Any], changes: dict[str, Any], *, schema_path: Any
) -> dict[str, Any]:
    """Update artifact-level descriptive fields (domain, mental model).

    Structural collections are not reachable from here for the same reason they
    are not reachable from an entity PATCH.
    """
    domain_fields = {"name", "scope", "target_user", "non_goals"}
    mental_model_fields = {"summary", "flow"}
    allowed = domain_fields | mental_model_fields
    unknown = sorted(set(changes) - allowed)
    if unknown:
        raise CopStudioError(
            "FIELD_NOT_EDITABLE",
            f"These fields cannot be edited by hand: {', '.join(unknown)}. "
            f"Editable fields are: {', '.join(sorted(allowed))}",
            status_code=422,
            details={"rejected": unknown, "editable": sorted(allowed)},
        )
    if not changes:
        raise CopStudioError("EMPTY_EDIT", "Provide at least one field to change", status_code=422)

    updated = copy.deepcopy(artifact)
    for field, value in changes.items():
        if field in domain_fields:
            section = updated.setdefault("domain", {})
        else:
            section = updated.setdefault("mental_model", {})
        if isinstance(section.get(field), list):
            if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
                raise CopStudioError(
                    "FIELD_TYPE_INVALID",
                    f"'{field}' must be a list of strings",
                    status_code=422,
                    details={"field": field},
                )
            section[field] = [item.strip() for item in value if item.strip()]
        else:
            if not isinstance(value, str) or not value.strip():
                raise CopStudioError(
                    "FIELD_REQUIRED" if field in ("name", "summary") else "FIELD_TYPE_INVALID",
                    f"'{field}' must be a non-empty string",
                    status_code=422,
                    details={"field": field},
                )
            section[field] = value.strip()

    _validate(updated, schema_path)
    return updated


def summarize(artifact: dict[str, Any]) -> dict[str, Any]:
    """Counts shown next to a draft so the user can see what they are editing."""
    domain = artifact.get("domain") or {}
    return {
        "title": domain.get("name", ""),
        "counts": {
            "goals": len(artifact.get("goals") or []),
            "processes": len(artifact.get("main_processes") or []),
            "stages": len(artifact.get("stages") or []),
            "concepts": len(artifact.get("concepts") or []),
            "operations": len(artifact.get("operations") or []),
            "shared_foundations": len(artifact.get("shared_foundations") or []),
            "practices": len(artifact.get("practices") or []),
        },
    }


def next_version_number(existing: list[int]) -> int:
    return (max(existing) + 1) if existing else 1


def new_draft_id() -> uuid.UUID:
    return uuid.uuid4()
