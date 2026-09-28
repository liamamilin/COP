"""H70 — Detect Branches and Shared Foundations.

Split responsibility on purpose:

- Branches are semantic, so the model proposes them.
- Shared Foundations are structural, so exact normalized-title comparison in
  this module decides them. Letting the model guess at stage equality would
  risk silently dropping a stage from the main line.
"""

from typing import Any

from app.harness.context import HarnessContext, HarnessEvent, StepResult
from app.harness.prompts import build_compression_prompt
from app.harness.schemas import COMPRESSION_SCHEMA

MIN_FOUNDATION_LENGTH = 2
FOUNDATION_KEY = "f_shared"


def detect_shared_foundation(
    processes: list[dict[str, Any]],
) -> tuple[dict[str, Any] | None, dict[str, dict[str, Any]], dict[str, list[str]]]:
    """Find a repeated leading Stage sequence shared by two or more processes.

    Returns (foundation, process_starts, process_stage_keys).
    """
    starts: dict[str, dict[str, Any]] = {
        process["key"]: {"type": "zero", "ref": None} for process in processes
    }
    stage_map: dict[str, list[str]] = {
        process["key"]: list(process["stage_keys"]) for process in processes
    }
    if len(processes) < 2:
        return None, starts, stage_map

    candidates: list[list[str]] = []
    longest = min(len(process["stage_keys"]) for process in processes)
    for length in range(longest, 0, -1):
        prefixes = [tuple(process["stage_keys"][:length]) for process in processes]
        if len(set(prefixes)) == 1:
            candidates = [list(prefixes[0])]
            break
    if not candidates:
        return None, starts, stage_map

    shared = candidates[0]
    if len(shared) < MIN_FOUNDATION_LENGTH:
        # A single leading stage is too small to justify a Foundation; keeping
        # it inline preserves traceability to Zero State.
        return None, starts, stage_map

    titles = _stage_titles(processes, shared)
    foundation = {
        "key": FOUNDATION_KEY,
        "title": "Shared Foundation",
        "stage_keys": list(shared),
        "stage_titles": titles,
    }
    for process in processes:
        key = process["key"]
        remaining = stage_map[key][len(shared) :]
        if not remaining:
            # A process that is only the foundation still needs its own stages.
            remaining = list(shared)
        stage_map[key] = remaining
        starts[key] = {"type": "foundation", "ref": FOUNDATION_KEY}
    return foundation, starts, stage_map


def _stage_titles(processes: list[dict[str, Any]], stage_keys: list[str]) -> list[str]:
    lookup = {
        stage["key"]: stage["title"] for process in processes for stage in process.get("stages", [])
    }
    return [lookup.get(key, key) for key in stage_keys]


def normalize_branches(
    payload: dict[str, Any],
    *,
    stage_keys: set[str],
    process_keys: set[str],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[str]]:
    """Keep only Branches whose parent actually exists."""
    alternative: list[dict[str, Any]] = []
    extension: list[dict[str, Any]] = []
    warnings: list[str] = []
    seen_keys: set[str] = set()

    for index, raw in enumerate(payload.get("alternative_branches") or [], start=1):
        title = str(raw.get("title", "")).strip()
        parent = str(raw.get("parent_stage_key", "")).strip()
        if not title or parent not in stage_keys:
            if title:
                warnings.append(
                    f"Dropped alternative Branch '{title}': its parent Stage is unknown"
                )
            continue
        key = f"b_alt_{parent}_{index}"
        while key in seen_keys:
            key = f"{key}_x"
        seen_keys.add(key)
        alternative.append(
            {
                "key": key,
                "type": "alternative",
                "title": title,
                "description": str(raw.get("description", "")).strip(),
                "parent_stage_key": parent,
            }
        )

    for index, raw in enumerate(payload.get("extension_branches") or [], start=1):
        title = str(raw.get("title", "")).strip()
        parent = str(raw.get("parent_process_key", "")).strip()
        if not title or parent not in process_keys:
            if title:
                warnings.append(
                    f"Dropped extension Branch '{title}': its parent process is unknown"
                )
            continue
        key = f"b_ext_{parent}_{index}"
        while key in seen_keys:
            key = f"{key}_x"
        seen_keys.add(key)
        extension.append(
            {
                "key": key,
                "type": "extension",
                "title": title,
                "description": str(raw.get("description", "")).strip(),
                "parent_process_key": parent,
            }
        )
    return alternative, extension, warnings


class CompressionStep:
    name = "H70"

    async def execute(self, ctx: HarnessContext, services: Any) -> StepResult:
        processes = ctx.require("process_drafts")
        stage_keys = {key for process in processes for key in process["stage_keys"]}
        language = ctx.settings.get("language", "auto")

        system, user = build_compression_prompt(
            processes=processes, stage_count=len(stage_keys), language=language
        )
        payload = await services.complete_structured(
            system_prompt=system, user_prompt=user, schema=COMPRESSION_SCHEMA
        )

        alternative, extension, warnings = normalize_branches(
            payload,
            stage_keys=stage_keys,
            process_keys={process["key"] for process in processes},
        )
        foundation, starts, stage_map = detect_shared_foundation(processes)
        if foundation:
            warnings.append(
                f"Extracted a Shared Foundation of {len(foundation['stage_keys'])} stages "
                f"shared by {len(processes)} processes"
            )

        return StepResult.success(
            {
                "branches": alternative + extension,
                "foundations": [foundation] if foundation else [],
                "process_starts": starts,
                "process_stage_keys": stage_map,
            },
            events=[
                HarnessEvent(
                    "step.completed",
                    {
                        "step": self.name,
                        "branch_count": len(alternative) + len(extension),
                        "foundations": 1 if foundation else 0,
                    },
                )
            ],
            warnings=warnings,
            metrics={
                "branch_count": len(alternative) + len(extension),
                "foundation_count": 1 if foundation else 0,
            },
        )
