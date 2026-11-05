"""Experimental teaching contract, separate from the published COP schema.

Validation is structural and content-bound, not a semantic or learner grade.
There is deliberately no provider, database, subprocess, or network dependency.
"""

import ast
import hashlib
import json
from typing import Annotated, Any, Literal

from pydantic import BaseModel, ConfigDict, Field, StringConstraints, ValidationError

from app.domain.cop_models import COPArtifact

Text = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, pattern=r"\S")]
Texts = Annotated[list[Text], Field(min_length=1)]


class UnitModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class UnitBinding(UnitModel):
    artifact_sha256: Annotated[str, Field(pattern="^[a-f0-9]{64}$")]
    goal_ref: Text
    process_ref: Text


class LearningPath(UnitModel):
    id: Text
    label: Text
    description: Text
    goal_scope: Literal["partial", "full"]
    needs_network: bool
    may_cost: bool


class EntryResource(UnitModel):
    id: Text
    name: Text
    provenance: Text
    readiness_check: Text
    path_ids: list[Text]


class LearnerProfile(UnitModel):
    audience: Text
    prior_knowledge: Texts
    environment: Texts
    exclusions: Texts
    resources: Annotated[list[EntryResource], Field(min_length=1)]


class DetailRef(UnitModel):
    stage_ref: Text
    detail_index: Annotated[int, Field(ge=0)]


class UnitOutput(UnitModel):
    id: Text
    name: Text
    description: Text
    producer_stage_ref: Text
    kind: Literal["file", "value", "evidence", "private"]
    persistence: Literal["durable", "process"]
    format: Literal["python", "json", "text", "unspecified"]
    content_ref: DetailRef | None
    path_ids: list[Text]


class InputBinding(UnitModel):
    kind: Literal["entry", "output"]
    ref: Text
    why_needed: Text
    readiness_check: Text
    path_ids: list[Text]


class ConceptExplanation(UnitModel):
    concept_ref: Text
    plain_language: Text
    concrete_example: Text
    contrast: Text
    why_here: Text


class CausalLink(UnitModel):
    concept_ref: Text
    operation_ref: Text
    before: Text
    action: Text
    because: Text
    after: Text


class UnitMethod(UnitModel):
    detail_index: Annotated[int, Field(ge=0)]
    teaching_note: Text
    optional: bool
    path_ids: list[Text]


class WorkedCase(UnitModel):
    kind: Literal["illustration"]
    input_refs: Texts
    output_refs: Texts
    walkthrough: Texts
    observation: Text


class UnitCheck(UnitModel):
    output_ref: Text
    instruction: Text
    expected: Text
    why: Text
    limitation: Text
    on_failure: Text
    path_ids: list[Text]


class LearningQuestion(UnitModel):
    id: Text
    kind: Literal["predict", "explain", "diagnose", "transfer"]
    prompt: Text
    hints: list[Text]
    criteria: Texts
    stage_refs: Texts
    path_ids: list[Text]


class ReasoningMove(UnitModel):
    observation: Text
    inference: Text
    warrant: Text
    limitation: Text
    source_ids: Texts


class RouteExplanation(UnitModel):
    stage_ref: Text
    question: Text
    builds_on: list[Text]
    why_now: Text
    next_gap: Text


class UnitOrientation(UnitModel):
    question: Text
    why_this_route: Text
    running_case: Text
    case_facts: Texts
    case_unknowns: Texts
    route: Annotated[list[RouteExplanation], Field(min_length=1)]


class UnitStep(UnitModel):
    stage_ref: Text
    purpose: Text
    inputs: Annotated[list[InputBinding], Field(min_length=1)]
    concepts: Annotated[list[ConceptExplanation], Field(min_length=1)]
    causal_chain: Annotated[list[CausalLink], Field(min_length=1)]
    methods: Annotated[list[UnitMethod], Field(min_length=1)]
    output_refs: Texts
    worked_case: WorkedCase
    checks: Annotated[list[UnitCheck], Field(min_length=1)]
    practice: LearningQuestion
    reasoning: list[ReasoningMove] = Field(default_factory=list)


class UnitSource(UnitModel):
    id: Text
    title: Text
    url: Text
    scope: Text


class LearningUnit(UnitModel):
    schema_version: Literal["0.1-experimental"]
    unit_id: Text
    title: Text
    outcome: Text
    task_brief: Text
    binding: UnitBinding
    profile: LearnerProfile
    paths: Annotated[list[LearningPath], Field(min_length=1)]
    outputs: Annotated[list[UnitOutput], Field(min_length=1)]
    steps: Annotated[list[UnitStep], Field(min_length=1)]
    assessment: Annotated[list[LearningQuestion], Field(min_length=3)]
    sources: Annotated[list[UnitSource], Field(min_length=1)]
    limitations: Texts
    orientation: UnitOrientation | None = None


def content_hash(value: Any) -> str:
    """sha256(canonical-json-v1): sorted ASCII field keys; array order retained."""
    encoded = json.dumps(
        value, sort_keys=True, ensure_ascii=False, separators=(",", ":"), allow_nan=False,
    )
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


def check_learning_unit(raw: dict[str, Any], artifact: dict[str, Any]) -> list[dict[str, str]]:
    """Reject mechanical teaching gaps; never certify facts/execution/learning."""
    issues: list[dict[str, str]] = []

    def issue(code: str, ref: str, message: str) -> None:
        issues.append({"code": code, "ref": ref, "message": message})

    try:
        unit = LearningUnit.model_validate(raw)
    except ValidationError as error:
        return [{"code": "UNIT_SCHEMA", "ref": "/".join(map(str, item["loc"])),
                 "message": item["msg"]} for item in error.errors()]

    try:
        COPArtifact.model_validate(artifact)
    except ValidationError as error:
        return [{"code": "ARTIFACT_SCHEMA", "ref": "/".join(map(str, item["loc"])),
                 "message": item["msg"]} for item in error.errors()]

    if unit.binding.artifact_sha256 != content_hash(artifact):
        issue("STALE_ARTIFACT", "binding", "Teaching belongs to a different artifact revision.")
    processes = {item["id"]: item for item in artifact.get("main_processes", [])}
    process = processes.get(unit.binding.process_ref)
    if not process or process.get("goal_ref") != unit.binding.goal_ref:
        issue("UNIT_TARGET", "binding", "Goal/process binding does not resolve.")
        return issues
    foundation = next((item for item in artifact.get("shared_foundations", [])
                       if item["id"] == process.get("start", {}).get("ref")), None)
    expected_order = [*(foundation or {}).get("stage_refs", []), *process.get("stage_refs", [])]
    order = [step.stage_ref for step in unit.steps]
    if order != expected_order:
        issue("UNIT_ROUTE", "steps", "The full foundation/process order must be covered exactly.")
    if len(set(order)) != len(order):
        issue("DUPLICATE_STAGE", "steps", "A teaching step appears more than once.")
    positions = {ref: index for index, ref in enumerate(order)}
    stages = {item["id"]: item for item in artifact.get("stages", [])}
    operations = {item["id"]: item for item in artifact.get("operations", [])}
    path_ids = {path.id for path in unit.paths}

    def paths(values: list[str], ref: str) -> set[str]:
        if len(values) != len(set(values)):
            issue("DUPLICATE_PATH", ref, "A path id is repeated.")
        if set(values) - path_ids:
            issue("UNKNOWN_PATH", ref, "A path id is not declared by this unit.")
        return set(values) or path_ids

    def unique(items: list[Any], label: str) -> dict[str, Any]:
        result = {}
        for item in items:
            if item.id in result:
                issue("DUPLICATE_ID", item.id, f"Duplicate {label} id.")
            result[item.id] = item
        return result

    unique(unit.paths, "path")
    unique(unit.sources, "source")
    resources = unique(unit.profile.resources, "entry resource")
    outputs = unique(unit.outputs, "output")
    if resources.keys() & outputs.keys():
        issue("DUPLICATE_ID", "outputs", "Entry and output ids must be distinct.")
    lessons = {step.stage_ref: step for step in unit.steps}
    source_ids = {source.id for source in unit.sources}
    if unit.orientation:
        route = unit.orientation.route
        if [item.stage_ref for item in route] != order:
            issue("TEACHING_ROUTE", "orientation",
                  "Explanations must cover the same ordered route.")
        for item in route:
            if len(set(item.builds_on)) != len(item.builds_on):
                issue("TEACHING_PREREQUISITE", item.stage_ref, "A prerequisite is repeated.")
            for ref in item.builds_on:
                if (ref not in positions or item.stage_ref not in positions
                        or positions[ref] >= positions[item.stage_ref]):
                    issue("TEACHING_PREREQUISITE", item.stage_ref,
                          "Teaching prerequisites must name earlier steps in this route.")
        if not all(step.reasoning for step in unit.steps):
            issue("MISSING_REASONING", "steps", "An oriented unit needs reasoning for every step.")
    for resource in resources.values():
        paths(resource.path_ids, resource.id)
    for output in outputs.values():
        paths(output.path_ids, output.id)
        producer = lessons.get(output.producer_stage_ref)
        if not producer or output.id not in producer.output_refs:
            issue("MISSING_PRODUCER", output.id, "No lesson declares this produced output.")
        if output.kind == "file" and output.content_ref is None:
            issue("MISSING_FILE_CONTENT", output.id, "An authored file needs its complete content.")
        if output.kind == "private" and output.content_ref is not None:
            issue("PRIVATE_CONTENT", output.id, "Private learner values must not be embedded.")
        if output.content_ref:
            ref = output.content_ref
            details = stages.get(ref.stage_ref, {}).get("implementation_details", [])
            if ref.stage_ref != output.producer_stage_ref or ref.detail_index >= len(details):
                issue("CONTENT_REF", output.id, "File content does not resolve to its producer.")
                continue
            content = details[ref.detail_index].get("command", "")
            if not content.strip():
                issue("MISSING_FILE_CONTENT", output.id, "The content reference has no file body.")
            elif output.format in {"python", "json"}:
                try:
                    ast.parse(content) if output.format == "python" else json.loads(content)
                except (SyntaxError, ValueError, TypeError):
                    issue("INVALID_FILE_CONTENT", output.id,
                          "The referenced text is not a complete parseable file of this format.")
            matching = [method for method in (producer.methods if producer else [])
                        if method.detail_index == ref.detail_index and not method.optional]
            coverage = set().union(*(paths(method.path_ids, output.id) for method in matching))
            if not paths(output.path_ids, output.id) <= coverage:
                issue("UNREACHABLE_FILE_METHOD", output.id,
                      "Some paths do not provide the mandatory method that supplies this file.")

    question_ids: set[str] = set()

    def question(item: LearningQuestion) -> None:
        if item.id in question_ids:
            issue("DUPLICATE_QUESTION", item.id, "Practice/assessment ids must be unique.")
        question_ids.add(item.id)
        paths(item.path_ids, item.id)
        if set(item.stage_refs) - set(order):
            issue("QUESTION_REF", item.id, "Question points outside this learning unit.")
        if len(item.stage_refs) != len(set(item.stage_refs)):
            issue("QUESTION_REF", item.id, "A question repeats the same stage reference.")

    for step in unit.steps:
        stage = stages.get(step.stage_ref)
        if stage is None:
            issue("UNKNOWN_STAGE", step.stage_ref, "Stage does not exist in the source artifact.")
            continue
        for move in step.reasoning:
            if set(move.source_ids) - source_ids:
                issue("REASONING_SOURCE", step.stage_ref,
                      "Reasoning points to an undeclared source; citations do not verify facts.")
        for input_item in step.inputs:
            active = paths(input_item.path_ids, step.stage_ref)
            source = (resources if input_item.kind == "entry" else outputs).get(input_item.ref)
            if source is None:
                issue("MISSING_INPUT", step.stage_ref, f"Unresolved input: {input_item.ref}")
                continue
            if not active <= paths(source.path_ids, input_item.ref):
                issue("INPUT_PATH_GAP", step.stage_ref, "Input is unavailable on a declared path.")
            if input_item.kind == "output":
                producer_position = positions.get(source.producer_stage_ref, len(order))
                if producer_position >= positions[step.stage_ref]:
                    issue("FORWARD_INPUT", step.stage_ref,
                          "Input must be produced by an earlier step.")
                if source.persistence == "process":
                    issue("EPHEMERAL_HANDOFF", input_item.ref,
                          "An in-memory object cannot be handed to a different process/step.")
        explained = {item.concept_ref for item in step.concepts}
        if len(explained) != len(step.concepts):
            issue("DUPLICATE_CONCEPT", step.stage_ref, "A concept explanation is repeated.")
        canonical = set(stage.get("concept_refs", []))
        if canonical - explained:
            issue("UNEXPLAINED_CONCEPT", step.stage_ref, "A load-bearing concept has no teaching.")
        if explained - canonical:
            issue("CONCEPT_REF", step.stage_ref,
                  "Concept explanation does not belong to this step.")
        for link in step.causal_chain:
            acted_on = operations.get(link.operation_ref, {}).get("acts_on_concept_refs", [])
            if (link.concept_ref not in explained
                    or link.operation_ref not in stage.get("operation_refs", [])
                    or link.concept_ref not in acted_on):
                issue("CAUSAL_REF", step.stage_ref,
                      "Concept/operation causal link does not resolve.")
        linked_operations = {link.operation_ref for link in step.causal_chain}
        if set(stage.get("operation_refs", [])) - linked_operations:
            issue("UNEXPLAINED_OPERATION", step.stage_ref, "An operation lacks its causal role.")
        if explained - {link.concept_ref for link in step.causal_chain}:
            issue("UNLINKED_CONCEPT", step.stage_ref,
                  "A concept has no causal link to an operation.")
        methods = stage.get("implementation_details", [])
        if set(range(len(methods))) - {method.detail_index for method in step.methods}:
            issue("UNCOVERED_METHOD", step.stage_ref, "A saved instruction has no path mapping.")
        for method in step.methods:
            paths(method.path_ids, step.stage_ref)
            if method.detail_index >= len(methods):
                issue("METHOD_REF", step.stage_ref, "Method index is outside the source stage.")
            elif not (methods[method.detail_index].get("action", "").strip()
                      or methods[method.detail_index].get("command", "").strip()):
                issue("EMPTY_METHOD", step.stage_ref, "A title alone is not a method.")
        for ref in step.output_refs:
            if ref not in outputs or outputs[ref].producer_stage_ref != step.stage_ref:
                issue("OUTPUT_REF", step.stage_ref,
                      "Output belongs to a different or missing step.")
        if len(set(step.output_refs)) != len(step.output_refs):
            issue("DUPLICATE_OUTPUT", step.stage_ref, "An output is declared twice by this step.")
        input_refs = {item.ref for item in step.inputs}
        if set(step.worked_case.input_refs) != input_refs:
            issue("EXAMPLE_INPUT", step.stage_ref, "Worked case does not use this step's inputs.")
        if set(step.worked_case.output_refs) != set(step.output_refs):
            issue("EXAMPLE_OUTPUT", step.stage_ref, "Worked case changes the task/output contract.")
        checked: dict[str, set[str]] = {}
        for check in step.checks:
            if check.output_ref not in step.output_refs:
                issue("CHECK_REF", step.stage_ref, "Check points outside this step's outputs.")
            check_paths = paths(check.path_ids, step.stage_ref)
            if check.output_ref in outputs and not check_paths <= paths(
                outputs[check.output_ref].path_ids, check.output_ref,
            ):
                issue("CHECK_PATH_GAP", step.stage_ref,
                      "A check requires an output unavailable on this path.")
            checked.setdefault(check.output_ref, set()).update(check_paths)
        for ref in step.output_refs:
            if ref in outputs and not paths(outputs[ref].path_ids, ref) <= checked.get(ref, set()):
                issue("UNCHECKED_OUTPUT", ref, "An output lacks a check on one or more paths.")
        question(step.practice)
        if step.stage_ref not in step.practice.stage_refs:
            issue("PRACTICE_REF", step.stage_ref, "Practice must concern its own step.")
        for path_id in path_ids:
            if not any(path_id in paths(item.path_ids, step.stage_ref) for item in step.inputs):
                issue("STEP_INPUT_GAP", step.stage_ref, "A path has no declared starting input.")
            if not any(not item.optional and path_id in paths(item.path_ids, step.stage_ref)
                       for item in step.methods):
                issue("STEP_METHOD_GAP", step.stage_ref, "A path has no mandatory method.")
            if not any(ref in outputs and path_id in paths(outputs[ref].path_ids, ref)
                       for ref in step.output_refs):
                issue("STEP_OUTPUT_GAP", step.stage_ref, "A path produces no declared output.")
            if path_id not in paths(step.practice.path_ids, step.practice.id):
                issue("PRACTICE_PATH_GAP", step.stage_ref, "A path has no practice for this step.")
    for item in unit.assessment:
        question(item)
    for path_id in path_ids:
        kinds = {item.kind for item in unit.assessment
                 if path_id in paths(item.path_ids, item.id)}
        if not {"explain", "diagnose", "transfer"} <= kinds:
            issue("ASSESSMENT_GAP", path_id, "Explain, diagnose and transfer must all be assessed.")
    return issues


def unit_manifest(unit: dict[str, Any], artifact: dict[str, Any]) -> dict[str, Any]:
    return {
        "checker_version": "learning-unit-contract/0.1",
        "scope": "structure-and-bindings-only",
        "hash_algorithm": "sha256-canonical-json-v1",
        "unit_sha256": content_hash(unit),
        "artifact_sha256": content_hash(artifact),
        "issues": check_learning_unit(unit, artifact),
        "not_verified": ["semantic correctness", "live execution", "learner understanding",
                         "transfer performance", "automatic generation stability"],
    }
