"""Deterministic mock provider that emits structurally valid step output.

The mock exists so the full Harness chain can be developed and tested without a
paid API. It is not a stub: it synthesizes a real, referentially consistent COP
from the intake payload, which means M4 acceptance (`topic -> run -> validated
candidate COP`) can be exercised in mock mode.

Every response is a pure function of the prompt payload, so two runs with the
same inputs produce byte-identical output.
"""

import hashlib
import re
from typing import Any

from app.harness.prompts import decode_payload
from app.harness.providers.base import ProviderError
from app.harness.schemas import CRITIC_ISSUE_CODES

_STAGE_TEMPLATES = (
    ("Prepare the environment", "a runnable baseline for {domain}"),
    ("Establish the core object", "a validated {domain} core object"),
    ("Connect the first capability", "an end-to-end {domain} capability"),
    ("Handle the common failure", "a recoverable {domain} failure path"),
    ("Verify observable behavior", "a verified {domain} result"),
)

_OPERATION_TEMPLATES = (
    ("configure", "Set up the {domain} runtime so later steps can rely on it."),
    ("build", "Assemble the {domain} objects into a working unit."),
    ("connect", "Link the {domain} components into an executable path."),
    ("validate", "Check the {domain} result against an observable expectation."),
)

_CONCEPT_TEMPLATES = (
    ("Runtime", "The environment that hosts {domain} execution."),
    ("Core Object", "The primary unit {domain} operates on."),
    ("Capability", "A behavior {domain} can perform once wired correctly."),
)


def _digest(*parts: str) -> str:
    return hashlib.sha256("|".join(parts).encode()).hexdigest()


def _clean(value: Any, fallback: str) -> str:
    if isinstance(value, str) and value.strip():
        return value.strip()
    return fallback


def _domain_name(payload: dict[str, Any]) -> str:
    scope = payload.get("scope")
    if isinstance(scope, dict) and scope.get("domain"):
        return str(scope["domain"])
    for candidate in (payload.get("topic"), payload.get("goal")):
        if isinstance(candidate, str) and candidate.strip():
            return candidate.strip()
    return "Untitled Domain"


def _topic(payload: dict[str, Any]) -> str:
    value = _clean(payload.get("topic"), "")
    if value:
        return value
    goal = payload.get("goal")
    if isinstance(goal, dict):
        return _clean(goal.get("title"), "Capability")
    return _clean(payload.get("domain"), "Domain")


def _language(payload: dict[str, Any]) -> str:
    return _clean(payload.get("language"), "en")


def _mock_intake(payload: dict[str, Any]) -> dict[str, Any]:
    topic = _clean(payload.get("topic"), "")
    if not topic and not payload.get("sources"):
        return {"invalid": True}
    return {
        "topic": topic or _clean((payload.get("scope") or {}).get("domain"), "Untitled Domain"),
        "scope_hint": _clean(payload.get("scope_hint"), ""),
        "target_outcomes": list(payload.get("target_outcomes") or []),
        "learner_level": _clean(payload.get("learner_level"), "new"),
        "language": _language(payload),
        "depth": _clean(payload.get("depth"), "standard"),
        "source_ids": [
            str(item.get("id"))
            for item in payload.get("sources") or []
            if isinstance(item, dict) and item.get("id")
        ],
    }


def _mock_scope(payload: dict[str, Any]) -> dict[str, Any]:
    topic = _clean(payload.get("topic"), "Untitled Domain")
    hint = _clean(payload.get("scope_hint"), "")
    outcomes = payload.get("target_outcomes") or []
    scope = hint or f"Build and operate {topic} through its primary workflow."
    if outcomes:
        scope = f"{scope} Target outcomes: {'; '.join(str(item) for item in outcomes)}."
    return {
        "domain": topic,
        "scope": scope,
        "target_user": (
            f"A {payload.get('learner_level', 'new')} practitioner who needs to act in {topic}."
        ),
        "non_goals": [
            f"Exhaustive reference of every {topic} feature",
            "Vendor-specific configuration trivia",
        ],
        "ambiguity_notes": [],
    }


def _mock_brief(payload: dict[str, Any]) -> dict[str, Any]:
    scope = payload.get("scope") or {}
    sources = payload.get("sources") or []
    domain = _clean(scope.get("domain"), _domain_name(payload))
    evidence_index = [
        {
            "source_id": str(item.get("id")),
            "segment_id": f"seg:{_digest(str(item.get('id')))[:8]}",
        }
        for item in sources
        if isinstance(item, dict) and item.get("id")
    ]
    return {
        "domain_purpose": _clean(
            scope.get("scope"), f"Give a practitioner a usable path through {domain}."
        ),
        "capability_candidates": [
            f"Produce a working {domain} result",
            f"Recover from the most common {domain} failure",
            f"Verify {domain} behavior against an observable expectation",
        ],
        "workflow_candidates": [
            f"Prepare -> Build -> Connect -> Validate for {domain}",
        ],
        "structural_terms": ["Runtime", "Core Object", "Capability"],
        "constraints": [],
        "version_specific_facts": [],
        "evidence_index": evidence_index,
    }


def _mock_goals(payload: dict[str, Any]) -> dict[str, Any]:
    scope = payload.get("scope") or {}
    brief = payload.get("brief") or {}
    domain = _clean(scope.get("domain"), "Domain")
    outcomes = list(payload.get("requested_outcomes") or [])
    candidates = [str(item) for item in brief.get("capability_candidates") or []]
    if outcomes:
        candidates = [f"Be able to {str(item).lower()}" for item in outcomes] + candidates
    candidates.append(f"Operate a complete {domain} workflow end to end")
    candidates.append(f"Recover a failed {domain} run without losing work")

    seen: set[str] = set()
    goals: list[dict[str, Any]] = []
    for index, candidate in enumerate(candidates, start=1):
        key = f"g{index}"
        if key in seen:
            continue
        seen.add(key)
        goals.append(
            {
                "key": key,
                "title": candidate.rstrip("."),
                "outcome": f"A verifiable {domain} result exists for: {candidate.rstrip('.')}.",
                "why_it_matters": (
                    f"Without this capability the {domain} workflow cannot be trusted in practice."
                ),
                "prerequisite_goal_keys": [f"g{index - 1}"] if index > 1 else [],
                "evidence_refs": [],
            }
        )
    return {"goals": goals}


def _mock_processes(payload: dict[str, Any]) -> dict[str, Any]:
    goal = payload.get("goal") or {}
    scope = payload.get("scope") or {}
    domain = _clean(scope.get("domain"), "Domain")
    goal_key = _clean(goal.get("key"), "g1")
    outcome = _clean(goal.get("outcome"), f"A working {domain} result.")
    stage_count = 4
    stages = [
        {
            "key": f"{goal_key}_s{index}",
            "title": title.format(domain=domain),
            "local_outcome": f"Reach a state where you have {detail.format(domain=domain)}.",
        }
        for index, (title, detail) in enumerate(_STAGE_TEMPLATES[:stage_count], start=1)
    ]
    return {
        "key": f"p_{goal_key}",
        "title": f"Deliver {goal.get('title', domain) if isinstance(goal, dict) else domain}",
        "outcome": outcome,
        "stages": stages,
    }


def _mock_detail(domain: str, title: str) -> dict[str, Any]:
    """One followable step, in the same shape a real provider must return.

    The mock exists so the acceptance path can run without an API key, and that
    only works if it honours the same content contract. A mock that emitted
    `{"label": ..., "body": ...}` while the schema demanded `title`/`action`
    would make the whole suite green and the real product broken.
    """
    return {
        "title": f"Carry out {title.lower()}",
        "action": f"Run the {title.lower()} step against your {domain} workspace.",
        "command": f"cop {title.lower().replace(' ', '-')}",
        "expected_result": f"The command exits 0 and the {domain} state is observable.",
        "caution": f"Confirm the {domain} environment is active before running it.",
    }


def _mock_stages(payload: dict[str, Any]) -> dict[str, Any]:
    process = payload.get("process") or {}
    stages = payload.get("stages") or []
    domain = _clean((payload.get("scope") or {}).get("domain"), "Domain")
    process_key = _clean(process.get("key"), "p_g1")
    enriched: list[dict[str, Any]] = []
    # The run's real source ids, so citations resolve. `payload_block` sends the
    # scope and stage keys rather than the bundle, so the ids are read from
    # whichever key the prompt carried them on.
    source_ids = [
        str(item)
        for item in (
            payload.get("source_ids") or (payload.get("scope") or {}).get("source_ids") or []
        )
        if str(item).strip()
    ]
    for index, stage in enumerate(stages, start=1):
        key = _clean(stage.get("key"), f"{process_key}_s{index}")
        title = _clean(stage.get("title"), f"Stage {index}")
        local_outcome = _clean(
            stage.get("local_outcome"), f"Obtain the {title} result in {domain}."
        )
        concept_keys = _CONCEPT_TEMPLATES[index % len(_CONCEPT_TEMPLATES) :]
        concept_keys += _CONCEPT_TEMPLATES[: index % len(_CONCEPT_TEMPLATES)]
        operation_keys = _OPERATION_TEMPLATES[index % len(_OPERATION_TEMPLATES) :]
        operation_keys += _OPERATION_TEMPLATES[: index % len(_OPERATION_TEMPLATES)]
        enriched.append(
            {
                "key": key,
                "title": title,
                "local_goal": f"Complete {title.lower()} for {domain}.",
                "why_it_exists": (
                    f"{title} is the step that turns intent into an observable {domain} state."
                ),
                "local_outcome": local_outcome,
                "dependency_notes": [] if index == 1 else [f"Requires stage {index - 1}."],
                "concept_candidates": [item[0] for item in concept_keys],
                "operation_candidates": [item[0] for item in operation_keys],
                "implementation_detail_candidates": [_mock_detail(domain, title)],
                "example_candidate": {
                    "summary": f"Apply {title.lower()} to a minimal {domain} case.",
                    "input": f"A single representative {domain} input.",
                    "output": f"The expected observable {domain} result.",
                },
                # Cites the sources the run actually read, so the generated
                # artifact demonstrates an evidence chain the user can open. An
                # empty list would make every Stage look unsourced, and the
                # golden case could not prove the citation path works.
                "evidence_refs": _evidence_for(source_ids, index),
            }
        )
    return {"stages": enriched}


def _evidence_for(source_ids: list[str], index: int) -> list[dict[str, str]]:
    """One citation, rotating through the run's real sources.

    Rotating rather than citing all of them on every Stage: a Stage carrying five
    references reads as though every sentence were contested, which is the
    Encyclopedia Failure in a different costume.
    """
    if not source_ids:
        return []
    source_id = source_ids[(index - 1) % len(source_ids)]
    return [{"source_id": source_id, "quote_hint": "Supporting passage in the source"}]


def _mock_canonicalize(payload: dict[str, Any]) -> dict[str, Any]:
    stages = payload.get("stages") or []
    domain = _domain_name({"scope": {"domain": "Domain"}})
    concept_keys: list[str] = []
    operation_keys: list[str] = []
    definitions: dict[str, dict[str, str]] = {}

    for stage in stages:
        for name in stage.get("concept_candidates") or []:
            key = f"c_{re.sub(r'[^a-z0-9]+', '_', str(name).lower()).strip('_')}"
            if key not in definitions:
                concept_keys.append(key)
                definitions[key] = {
                    "name": str(name),
                    "definition": _clean(
                        next(
                            (
                                item[1]
                                for item in _CONCEPT_TEMPLATES
                                if item[0].lower() == str(name).lower()
                            ),
                            f"A structural object that {domain} depends on.",
                        ),
                        "",
                    ),
                    "role": f"Required to understand and operate {domain}.",
                }
        for name in stage.get("operation_candidates") or []:
            key = f"o_{re.sub(r'[^a-z0-9]+', '_', str(name).lower()).strip('_')}"
            if key in definitions:
                continue
            operation_keys.append(key)
            definitions[key] = {
                "name": str(name),
                "definition": _clean(
                    next(
                        (
                            item[1]
                            for item in _OPERATION_TEMPLATES
                            if item[0].lower() == str(name).lower()
                        ),
                        f"A meaningful {domain} action above raw API syntax.",
                    ),
                    "",
                ),
                "purpose": f"Advances the {domain} process by one verifiable step.",
            }

    stage_bindings = {
        str(stage.get("key")): {
            "concept_keys": [
                f"c_{re.sub(r'[^a-z0-9]+', '_', str(name).lower()).strip('_')}"
                for name in stage.get("concept_candidates") or []
            ],
            "operation_keys": [
                f"o_{re.sub(r'[^a-z0-9]+', '_', str(name).lower()).strip('_')}"
                for name in stage.get("operation_candidates") or []
            ],
        }
        for stage in stages
    }

    concepts = [
        {
            "key": key,
            "name": definitions[key]["name"],
            "definition": definitions[key]["definition"],
            "role": definitions[key]["role"],
            "related_concept_keys": [],
            "key_operation_keys": operation_keys[:1],
        }
        for key in concept_keys
    ]
    operations = [
        {
            "key": key,
            "name": definitions[key]["name"],
            "definition": definitions[key]["definition"],
            "purpose": definitions[key]["purpose"],
            "acts_on_concept_keys": concept_keys[:1],
            # An Operation with no failure mode tells a beginner nowhere to look
            # when the thing they were told to do does not work.
            "common_failures": [
                f"Running '{definitions[key]['name'].lower()}' before its prerequisite is complete",
                "Assuming the step succeeded without checking the resulting state",
            ],
        }
        for key in operation_keys
    ]
    return {
        "concepts": concepts,
        "operations": operations,
        "stage_bindings": stage_bindings,
    }


def _mock_compression(payload: dict[str, Any]) -> dict[str, Any]:
    """Propose Branches only.

    Shared Foundations are computed by the harness, so the mock does not
    pretend to detect them.
    """
    processes = payload.get("processes") or []
    alternative = [
        {
            "key": f"b_alt_{index}",
            "title": (
                f"Alternative approach to the first stage of {process.get('title', 'the process')}"
            ),
            "description": "A different implementation that reaches the same local outcome.",
            "parent_stage_key": (process.get("stage_keys") or [""])[0],
        }
        for index, process in enumerate(processes, start=1)
        if process.get("stage_keys")
    ]
    extension = [
        {
            "key": f"b_ext_{index}",
            "title": f"Extend {process.get('title', 'the process')}",
            "description": "An optional capability that can be attached after the main result.",
            "parent_process_key": str(process.get("key")),
        }
        for index, process in enumerate(processes[:1], start=1)
    ]
    return {"alternative_branches": alternative, "extension_branches": extension}


def _mock_learning(payload: dict[str, Any]) -> dict[str, Any]:
    scope = payload.get("scope") or {}
    processes = payload.get("processes") or []
    domain = _clean(scope.get("domain"), "Domain")
    practices = (
        [
            {
                "key": f"pr_{index}",
                "title": f"Walk the {domain} main process",
                "process_key": str(process.get("key")),
                "instructions": [
                    f"Complete stage {stage} without skipping its local outcome."
                    for stage in process.get("stage_keys") or []
                ],
                "expected_outcome": f"A verified {domain} result you can explain.",
                "checkpoint_questions": [
                    f"Why does {domain} need this stage order?",
                    f"Which {domain} object is the hardest to change?",
                ],
            }
            for index, process in enumerate(processes, start=1)
        ]
        if payload.get("practices_enabled", True)
        else []
    )
    return {
        "mental_model": {
            "summary": (
                f"{domain} moves from a prepared runtime, through a core object, to a "
                "connected capability that can be validated."
            ),
            "flow": ["Runtime", "Core Object", "Capability", "Verification"],
        },
        "practices": practices,
        # Two directions, because the content gate requires an Expansion Map of at
        # least two. One leaves the learner with a dead end, which is the whole
        # thing the Map exists to prevent.
        "expansion_map": [
            {
                "title": f"Advanced {domain} patterns",
                "description": "Explore scaling and failure-recovery patterns.",
                "from_goal_key": str(processes[0].get("goal_key")) if processes else None,
            },
            {
                "title": f"Measuring {domain} quality",
                "description": (
                    "Add tracing and evaluation so regressions in the process are visible "
                    "rather than inferred."
                ),
                "from_goal_key": str(processes[-1].get("goal_key")) if processes else None,
            },
        ],
    }


def _mock_critic(payload: dict[str, Any]) -> dict[str, Any]:
    artifact = payload.get("artifact") or {}
    issues: list[dict[str, Any]] = []
    if len(artifact.get("concepts") or []) > 12:
        issues.append(
            {
                "code": "ENCYCLOPEDIA_DRIFT",
                "entity_ref": "artifact",
                "explanation": (
                    "The Concept count suggests reference coverage rather than structure."
                ),
                "recommended_change": (
                    "Demote the least reused Concepts to implementation detail."
                ),
            }
        )
    if not artifact.get("practices"):
        issues.append(
            {
                "code": "WEAK_PRACTICE",
                "entity_ref": "artifact",
                "explanation": "No Minimal Practice is attached to any process.",
                "recommended_change": "Add one practice that traverses a full Main Process.",
            }
        )
    severity = "major" if len(issues) > 1 else ("minor" if issues else "pass")
    return {"severity": severity, "issues": issues}


def _mock_refine(payload: dict[str, Any]) -> dict[str, Any]:
    issues = payload.get("issues") or []
    locked = set(payload.get("locked_paths") or [])
    view = payload.get("artifact") or {}
    artifact = view.get("artifact") or view
    revisions: list[dict[str, Any]] = []
    for issue in issues:
        if issue.get("code") not in CRITIC_ISSUE_CODES:
            continue
        entity_ref = str(issue.get("entity_ref") or "")
        if entity_ref in locked:
            continue
        resolved = _resolve_issue_entity(artifact, issue)
        if resolved is None:
            continue
        entity_type, entity_key = resolved
        change = _clean(issue.get("recommended_change"), "")
        if not change:
            # No instruction, so there is no recommended text to echo.
            # Synthesise a deterministic rewrite rather than returning nothing:
            # a refiner that silently proposes nothing makes every review
            # screen look like a failure rather than like "nothing to change".
            change = _synthesise_refinement(artifact, entity_type, entity_key)
        if not change:
            continue
        revisions.append(
            {
                "entity_type": entity_type,
                "entity_key": entity_key,
                "field": "definition"
                if entity_type in {"concept", "operation"}
                else _refine_field(entity_type),
                "value": change,
            }
        )
    return {"revisions": revisions}


#: entity type -> the collection holding it, for resolving a critic issue.
ENTITY_COLLECTIONS: dict[str, str] = {
    "goal": "goals",
    "process": "main_processes",
    "stage": "stages",
    "concept": "concepts",
    "operation": "operations",
    "branch": "branches",
}


def _resolve_issue_entity(
    artifact: dict[str, Any], issue: dict[str, Any]
) -> tuple[str, str] | None:
    """Work out which entity an issue is about, as `(type, id)`.

    Resolved by matching `entity_ref` against the ids actually present rather
    than by splitting the string on a dot. Splitting only appeared to work because
    generated ids happen to start with their type -- `goal.ship_a_capability`
    splits into `goal` and `ship_a_capability`, which is not the id at all. It
    also could not work for a targeted prompt, where the id appears behind an
    extra `goal.` prefix, and for a scoped view there are no collections to search
    at all. Matching ids is the one rule that holds for every prompt shape.
    """
    entity_ref = str(issue.get("entity_ref") or "")
    if not entity_ref:
        return None

    target = artifact.get("target")
    if isinstance(target, dict) and str(target.get("entity_id")) == entity_ref:
        entity_type = str(target.get("entity_type") or "")
        if entity_type in ENTITY_COLLECTIONS:
            return (entity_type, entity_ref)

    declared = str(issue.get("entity_type") or "")
    if declared in ENTITY_COLLECTIONS:
        collection = ENTITY_COLLECTIONS[declared]
        if any(str(item.get("id")) == entity_ref for item in (artifact.get(collection) or [])):
            return (declared, entity_ref)
        # A targeted view carries the entity even when the collection is absent.
        if isinstance(target, dict) and isinstance(target.get("entity"), dict):
            return (declared, entity_ref)

    for entity_type, collection in ENTITY_COLLECTIONS.items():
        if any(str(item.get("id")) == entity_ref for item in (artifact.get(collection) or [])):
            return (entity_type, entity_ref)
    return None


def _target_entity(
    artifact: dict[str, Any], entity_type: str, entity_key: str
) -> dict[str, Any] | None:
    """Find the entity to rewrite, in whichever shape the prompt delivered it.

    Two shapes exist. A full H110 prompt carries the whole artifact and the
    entity is found in its collection. A targeted H140 prompt carries
    `targeted_artifact_view`, which is deliberately scoped to the one entity the
    run may touch -- there is no collection to search. Reading only the
    collection made every targeted refinement propose nothing, and the user saw
    a review screen with an empty diff and no explanation, which reads as a
    broken feature rather than as "nothing to change".
    """
    target = artifact.get("target")
    if isinstance(target, dict) and str(target.get("entity_type")) == entity_type:
        entity = target.get("entity")
        if isinstance(entity, dict) and str(entity.get("id")) == entity_key:
            return entity

    collection = ENTITY_COLLECTIONS.get(entity_type)
    if not collection:
        return None
    return next(
        (item for item in (artifact.get(collection) or []) if str(item.get("id")) == entity_key),
        None,
    )


def _synthesise_refinement(artifact: dict[str, Any], entity_type: str, entity_key: str) -> str:
    """Rewrite a field the way a real refiner would, without a model call.

    Deterministic on purpose: the mock has to produce the same proposal every
    run so a before/after diff is reviewable rather than noisy.
    """
    entity = _target_entity(artifact, entity_type, entity_key)
    if entity is None:
        return ""
    field = _refine_field(entity_type)
    current = entity.get(field)
    if not isinstance(current, str) or not current.strip():
        return ""
    return f"{current.rstrip('.')} — stated so you can check it against a real run."


def _refine_field(entity_type: str) -> str:
    """The field a targeted refinement should rewrite for this entity type.

    A refinement has to change something the user can review, so it picks a
    prose field rather than a title: a diff on a paragraph is meaningful, a diff
    on a two-word title usually is not.
    """
    return {
        "goal": "why_it_matters",
        "process": "outcome",
        "stage": "why_it_exists",
    }.get(entity_type, "why_it_exists")


def _mock_repair(payload: dict[str, Any]) -> dict[str, Any]:
    """Echo the artifact back.

    The mock cannot repair broken references, so echoing makes the repair step
    converge immediately: validation either passes, or it was already invalid
    and the run correctly lands in `needs_attention`.
    """
    artifact = payload.get("artifact")
    return artifact if isinstance(artifact, dict) else {"invalid": True}


_DISPATCH = {
    "H00Intake": _mock_intake,
    "H10ScopeResolution": _mock_scope,
    "H20ResearchBrief": _mock_brief,
    "H30GoalExtraction": _mock_goals,
    "H40MainProcessConstruction": _mock_processes,
    "H50StageEnrichment": _mock_stages,
    "H60CanonicalizeConceptsOperations": _mock_canonicalize,
    "H70BranchFoundationCompression": _mock_compression,
    "H80LearningLayer": _mock_learning,
    "H100Critic": _mock_critic,
    "H110Refine": _mock_refine,
    "H120RepairArtifact": _mock_repair,
}


class MockProvider:
    """Deterministic provider used for development, CI, and acceptance runs."""

    def __init__(self, scenario: str = "success") -> None:
        self.scenario = scenario

    async def _simulate(self) -> None:
        if self.scenario == "timeout":
            raise ProviderError("PROVIDER_TIMEOUT", "Mock provider timed out", retryable=True)
        if self.scenario == "rate_limit":
            raise ProviderError(
                "PROVIDER_RATE_LIMITED", "Mock provider rate limited", retryable=True
            )

    async def health_check(self) -> dict[str, Any]:
        await self._simulate()
        return {"ok": True, "provider": "mock", "scenario": self.scenario}

    async def generate_structured(
        self, *, system_prompt: str, user_prompt: str, schema: dict[str, Any]
    ) -> dict[str, Any]:
        await self._simulate()
        if self.scenario == "invalid":
            return {"invalid": True}
        handler = _DISPATCH.get(str(schema.get("title")))
        if handler is None:
            return {"mock": True, "schema_title": schema.get("title")}
        return handler(decode_payload(user_prompt))

    async def generate_text(self, *, system_prompt: str, user_prompt: str) -> str:
        await self._simulate()
        return f"Mock response ({len(system_prompt)}:{len(user_prompt)})"
