from typing import Any, Literal, Self

from pydantic import BaseModel, ConfigDict, Field, model_validator


class COPModel(BaseModel):
    model_config = ConfigDict(extra="allow")


class EvidenceRef(COPModel):
    source_id: str
    segment_id: str | None = None
    quote_hint: str | None = None


class DomainInfo(COPModel):
    name: str
    scope: str
    target_user: str
    non_goals: list[str] = Field(default_factory=list)


class MentalModel(COPModel):
    summary: str
    flow: list[str] = Field(default_factory=list)


class Goal(COPModel):
    id: str
    title: str
    outcome: str
    why_it_matters: str = ""
    prerequisite_goal_refs: list[str] = Field(default_factory=list)
    evidence_refs: list[EvidenceRef] = Field(default_factory=list)


class SharedFoundation(COPModel):
    id: str
    title: str
    stage_refs: list[str]


class ProcessStart(COPModel):
    model_config = ConfigDict(extra="forbid")
    type: Literal["zero", "foundation"]
    ref: str | None = None


class MainProcess(COPModel):
    id: str
    goal_ref: str
    title: str
    start: ProcessStart
    stage_refs: list[str]
    outcome: str
    practice_ref: str | None = None


class Stage(COPModel):
    id: str
    title: str
    local_goal: str
    why_it_exists: str = ""
    local_outcome: str = ""
    concept_refs: list[str]
    operation_refs: list[str]
    branch_refs: list[str] = Field(default_factory=list)
    implementation_details: list[dict[str, Any]] = Field(default_factory=list)
    example: dict[str, Any] | None = None
    evidence_refs: list[EvidenceRef] = Field(default_factory=list)


class Concept(COPModel):
    id: str
    name: str
    definition: str
    role: str
    related_concept_refs: list[str] = Field(default_factory=list)
    key_operation_refs: list[str] = Field(default_factory=list)


class Operation(COPModel):
    id: str
    name: str
    definition: str
    purpose: str = ""
    acts_on_concept_refs: list[str] = Field(default_factory=list)
    common_failures: list[str] = Field(default_factory=list)


class Branch(COPModel):
    id: str
    type: Literal["alternative", "extension"]
    title: str
    parent_stage_ref: str | None = None
    parent_process_ref: str | None = None
    description: str = ""


class Practice(COPModel):
    id: str
    title: str
    goal_ref: str
    instructions: list[str]
    expected_outcome: str
    checkpoint_questions: list[str] = Field(default_factory=list)


class ExpansionItem(COPModel):
    title: str
    description: str = ""
    from_goal_ref: str | None = None


class ArtifactMetadata(COPModel):
    language: str = "auto"
    generated_at: str = ""
    generator: str = ""
    source_ids: list[str] = Field(default_factory=list)


class COPArtifact(COPModel):
    schema_version: Literal["0.1"]
    artifact_id: str
    domain: DomainInfo
    mental_model: MentalModel
    goals: list[Goal]
    shared_foundations: list[SharedFoundation]
    main_processes: list[MainProcess]
    stages: list[Stage]
    concepts: list[Concept]
    operations: list[Operation]
    branches: list[Branch]
    practices: list[Practice]
    expansion_map: list[ExpansionItem]
    metadata: ArtifactMetadata

    @model_validator(mode="after")
    def validate_references(self) -> Self:
        collections = {
            "goal": self.goals,
            "foundation": self.shared_foundations,
            "process": self.main_processes,
            "stage": self.stages,
            "concept": self.concepts,
            "operation": self.operations,
            "branch": self.branches,
            "practice": self.practices,
        }
        ids: dict[str, set[str]] = {}
        all_ids: list[str] = []
        for name, entities in collections.items():
            entity_ids = [entity.id for entity in entities]
            if len(entity_ids) != len(set(entity_ids)):
                raise ValueError(f"duplicate {name} id")
            ids[name] = set(entity_ids)
            all_ids.extend(entity_ids)
        if len(all_ids) != len(set(all_ids)):
            raise ValueError("entity IDs must be globally unique")

        def require(ref: str | None, kind: str, location: str) -> None:
            if ref is not None and ref not in ids[kind]:
                raise ValueError(f"{location} references missing {kind}: {ref}")

        for goal in self.goals:
            for ref in goal.prerequisite_goal_refs:
                require(ref, "goal", goal.id)
        for foundation in self.shared_foundations:
            for ref in foundation.stage_refs:
                require(ref, "stage", foundation.id)
        for process in self.main_processes:
            require(process.goal_ref, "goal", process.id)
            if not process.stage_refs:
                raise ValueError(f"{process.id} must contain at least one Stage")
            for ref in process.stage_refs:
                require(ref, "stage", process.id)
            if process.start.type == "foundation":
                require(process.start.ref, "foundation", process.id)
            require(process.practice_ref, "practice", process.id)
        for stage in self.stages:
            for ref in stage.concept_refs:
                require(ref, "concept", stage.id)
            for ref in stage.operation_refs:
                require(ref, "operation", stage.id)
            for ref in stage.branch_refs:
                require(ref, "branch", stage.id)
        for concept in self.concepts:
            for ref in concept.related_concept_refs:
                require(ref, "concept", concept.id)
            for ref in concept.key_operation_refs:
                require(ref, "operation", concept.id)
        for operation in self.operations:
            for ref in operation.acts_on_concept_refs:
                require(ref, "concept", operation.id)
        for branch in self.branches:
            require(branch.parent_stage_ref, "stage", branch.id)
            require(branch.parent_process_ref, "process", branch.id)
        for practice in self.practices:
            require(practice.goal_ref, "goal", practice.id)
        for item in self.expansion_map:
            require(item.from_goal_ref, "goal", item.title)
        return self
