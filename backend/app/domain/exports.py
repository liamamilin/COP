"""Portable exports for immutable COP versions.

Exports are derived only from a published artifact. They never read a draft,
so a downloaded file is a stable record of the version named in its filename.
"""

import io
import json
import re
import unicodedata
import zipfile
from typing import Any


def safe_slug(value: str, fallback: str = "cop") -> str:
    ascii_value = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode()
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", ascii_value).strip("-").lower()
    return (slug[:80] or fallback).strip("-")


def json_export(artifact: dict[str, Any]) -> bytes:
    return (json.dumps(artifact, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode()


def _text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value.strip()
    if isinstance(value, dict):
        for key in ("summary", "description", "name", "title"):
            if isinstance(value.get(key), str):
                return value[key].strip()
        return json.dumps(value, ensure_ascii=False, sort_keys=True)
    return str(value).strip()


def _bullet(label: str, value: Any) -> str:
    rendered = _text(value)
    return f"- **{label}:** {rendered}" if rendered else ""


def _stage_markdown(
    stage: dict[str, Any],
    concepts: dict[str, dict[str, Any]],
    operations: dict[str, dict[str, Any]],
    branches: dict[str, dict[str, Any]],
    *,
    heading: str = "####",
) -> str:
    lines = [f"{heading} {stage.get('title', stage.get('id', 'Stage'))}", ""]
    lines.extend(
        item
        for item in (
            _bullet("Local goal", stage.get("local_goal")),
            _bullet("Why it exists", stage.get("why_it_exists")),
            _bullet("Local outcome", stage.get("local_outcome")),
        )
        if item
    )

    concept_items = [concepts.get(str(ref)) for ref in stage.get("concept_refs") or []]
    if any(concept_items):
        lines.extend(["", f"{heading}# Concepts", ""])
        for concept in concept_items:
            if concept:
                lines.append(
                    f"- **{concept.get('name', concept.get('id'))}:** "
                    f"{concept.get('definition', '')}"
                )

    operation_items = [operations.get(str(ref)) for ref in stage.get("operation_refs") or []]
    if any(operation_items):
        lines.extend(["", f"{heading}# Operations", ""])
        for operation in operation_items:
            if operation:
                purpose = f" — {operation['purpose']}" if operation.get("purpose") else ""
                lines.append(
                    f"- **{operation.get('name', operation.get('id'))}:** "
                    f"{operation.get('definition', '')}{purpose}"
                )

    details = stage.get("implementation_details") or []
    if details:
        lines.extend(["", f"{heading}# Implementation details", ""])
        for detail in details:
            detail_title = _text(detail.get("title") or detail.get("name"))
            lines.append(f"- **{detail_title}:** {_text(detail)}")

    if stage.get("example"):
        lines.extend(["", f"{heading}# Example", "", _text(stage["example"])])

    branch_items = [branches.get(str(ref)) for ref in stage.get("branch_refs") or []]
    if any(branch_items):
        lines.extend(["", f"{heading}# Branches", ""])
        for branch in branch_items:
            if branch:
                lines.append(
                    f"- **{branch.get('title', branch.get('id'))}** "
                    f"({branch.get('type', 'branch')}): {branch.get('description', '')}"
                )
    return "\n".join(lines).rstrip()


def markdown_export(artifact: dict[str, Any], *, version_number: int | None = None) -> str:
    domain = artifact.get("domain") or {}
    concepts = {str(item.get("id")): item for item in artifact.get("concepts") or []}
    operations = {str(item.get("id")): item for item in artifact.get("operations") or []}
    stages = {str(item.get("id")): item for item in artifact.get("stages") or []}
    branches = {str(item.get("id")): item for item in artifact.get("branches") or []}
    practices = {str(item.get("id")): item for item in artifact.get("practices") or []}
    foundations = {
        str(item.get("id")): item for item in artifact.get("shared_foundations") or []
    }

    title = domain.get("name") or "COP Artifact"
    lines = [f"# {title}", ""]
    if version_number is not None:
        lines.extend([f"> Published COP version {version_number}", ""])
    lines.extend(
        item
        for item in (
            _bullet("Scope", domain.get("scope")),
            _bullet("Target learner", domain.get("target_user")),
        )
        if item
    )
    non_goals = domain.get("non_goals") or []
    if non_goals:
        lines.extend(["", "## Non-goals", "", *[f"- {item}" for item in non_goals]])

    mental = artifact.get("mental_model") or {}
    lines.extend(["", "## Mental model", "", _text(mental.get("summary"))])
    if mental.get("flow"):
        lines.extend(["", " → ".join(str(item) for item in mental["flow"])])

    shared = list(foundations.values())
    if shared:
        lines.extend(["", "## Shared foundations", ""])
        for foundation in shared:
            names = [
                stages.get(str(ref), {}).get("title", str(ref))
                for ref in foundation.get("stage_refs") or []
            ]
            title = foundation.get("title", foundation.get("id"))
            lines.append(f"- **{title}:** {', '.join(names)}")

    goals = {str(item.get("id")): item for item in artifact.get("goals") or []}
    lines.extend(["", "## Goals and main processes"])
    for number, process in enumerate(artifact.get("main_processes") or [], start=1):
        goal = goals.get(str(process.get("goal_ref"))) or {}
        lines.extend(
            [
                "",
                f"### {number}. {goal.get('title', process.get('title', 'Goal'))}",
                "",
                _text(goal.get("outcome")),
            ]
        )
        if goal.get("why_it_matters"):
            lines.extend(["", f"**Why it matters:** {goal['why_it_matters']}"])
        lines.extend(["", f"**Main Process:** {process.get('title', '')}"])
        start = process.get("start") or {}
        if start.get("type") == "foundation":
            foundation = foundations.get(str(start.get("ref"))) or {}
            lines.append(f"**Starts from:** {foundation.get('title', start.get('ref'))}")
        else:
            lines.append("**Starts from:** Zero State")
        for stage_ref in process.get("stage_refs") or []:
            stage = stages.get(str(stage_ref))
            if stage:
                lines.extend(
                    ["", _stage_markdown(stage, concepts, operations, branches, heading="####")]
                )
        lines.extend(["", f"**Process outcome:** {process.get('outcome', '')}"])

        practice = practices.get(str(process.get("practice_ref")))
        if practice:
            lines.extend(["", "#### Minimal practice", "", f"**{practice.get('title', '')}**"])
            lines.extend(
                f"{index}. {instruction}"
                for index, instruction in enumerate(practice.get("instructions") or [], start=1)
            )
            lines.extend(["", f"**Expected outcome:** {practice.get('expected_outcome', '')}"])
            questions = practice.get("checkpoint_questions") or []
            if questions:
                lines.extend(["", "**Checkpoint questions**", *[f"- {item}" for item in questions]])

    expansion = artifact.get("expansion_map") or []
    if expansion:
        lines.extend(["", "## Expansion map", ""])
        for item in expansion:
            lines.append(f"- **{item.get('title', '')}:** {item.get('description', '')}")

    lines.extend(
        [
            "",
            "---",
            "",
            f"Schema: {artifact.get('schema_version', 'unknown')} · "
            f"Artifact: {artifact.get('artifact_id', 'unknown')}",
            "",
        ]
    )
    return "\n".join(lines)


def markdown_bundle(artifact: dict[str, Any], *, version_number: int) -> bytes:
    buffer = io.BytesIO()
    concepts = {str(item.get("id")): item for item in artifact.get("concepts") or []}
    operations = {str(item.get("id")): item for item in artifact.get("operations") or []}
    branches = {str(item.get("id")): item for item in artifact.get("branches") or []}
    stages = {str(item.get("id")): item for item in artifact.get("stages") or []}

    with zipfile.ZipFile(buffer, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("README.md", markdown_export(artifact, version_number=version_number))
        archive.writestr("artifact.json", json_export(artifact))
        for index, stage in enumerate(stages.values(), start=1):
            name = f"stages/{index:03d}-{safe_slug(str(stage.get('title') or stage.get('id')))}.md"
            archive.writestr(
                name,
                _stage_markdown(stage, concepts, operations, branches, heading="#") + "\n",
            )
        for folder, entities, label_key in (
            ("concepts", concepts.values(), "name"),
            ("operations", operations.values(), "name"),
        ):
            for index, entity in enumerate(entities, start=1):
                title = str(entity.get(label_key) or entity.get("id"))
                lines = [f"# {title}", ""]
                for key, value in entity.items():
                    if key not in {"id", label_key} and value not in (None, "", []):
                        lines.append(_bullet(key.replace("_", " ").title(), value))
                archive.writestr(
                    f"{folder}/{index:03d}-{safe_slug(title)}.md", "\n".join(lines) + "\n"
                )
    return buffer.getvalue()
