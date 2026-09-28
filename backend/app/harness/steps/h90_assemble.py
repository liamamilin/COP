"""H90 — Assemble Artifact.

Fully deterministic. No creative model call is allowed here: this step owns
final stable IDs, reference wiring, temporary-field removal, and reading order.
Keeping it code-only is what makes the artifact reproducible and diffable.
"""

import uuid
from typing import Any

from app.core.errors import HarnessError
from app.harness.context import HarnessContext, HarnessEvent, StepResult
from app.harness.ids import IdAllocator

SCHEMA_VERSION = "0.1"
GENERATOR = "cop-studio-harness"


class Assembler:
    """Builds a canonical COPArtifact from checkpoint state."""

    def __init__(self, context: HarnessContext) -> None:
        self.ctx = context
        self.ids = IdAllocator()
        self.goal_ids: dict[str, str] = {}
        self.process_ids: dict[str, str] = {}
        self.stage_ids: dict[str, str] = {}
        self.concept_ids: dict[str, str] = {}
        self.operation_ids: dict[str, str] = {}
        self.branch_ids: dict[str, str] = {}
        self.practice_ids: dict[str, str] = {}
        self.foundation_ids: dict[str, str] = {}

    def assemble(self) -> dict[str, Any]:
        scope = self.ctx.require("scope_result")
        mental_model = self.ctx.require("mental_model")
        goals = self.ctx.require("goals")
        processes = self.ctx.require("process_drafts")
        stages = self.ctx.require("stage_drafts")
        concepts = self.ctx.require("concepts")
        operations = self.ctx.require("operations")

        if not goals or not processes or not stages:
            raise HarnessError(
                "HARNESS_INCOMPLETE_CHECKPOINTS",
                "Goals, Main Processes, and Stages are all required to assemble an artifact",
            )

        self._allocate(goals, processes, stages, concepts, operations)

        stage_map = {stage["key"]: stage for stage in stages}
        bindings = dict(self.ctx.stage_bindings or {})
        practice_by_process = {item["process_key"]: item for item in self.ctx.practices}
        starts = dict(self.ctx.process_starts or {})
        stage_order = dict(self.ctx.process_stage_keys or {})

        artifact_stages = [
            self._build_stage(stage, bindings.get(stage["key"], {})) for stage in stages
        ]

        artifact_foundations = [
            {
                "id": self.foundation_ids.get(item["key"], item["key"]),
                "title": item.get("title", "Shared Foundation"),
                "stage_refs": [
                    self.stage_ids[key]
                    for key in item.get("stage_keys", [])
                    if key in self.stage_ids
                ],
            }
            for item in self.ctx.foundations
        ]

        artifact_processes = [
            self._build_process(
                process,
                starts=starts.get(process["key"], {"type": "zero", "ref": None}),
                stage_keys=stage_order.get(process["key"], process["stage_keys"]),
                stage_map=stage_map,
                practice=practice_by_process.get(process["key"]),
            )
            for process in processes
        ]

        artifact_branches = [
            {
                "id": self.branch_ids.get(branch["key"], branch["key"]),
                "type": branch["type"],
                "title": branch["title"],
                "description": branch.get("description", ""),
                "parent_stage_ref": self.stage_ids.get(branch.get("parent_stage_key", "")),
                "parent_process_ref": self.process_ids.get(branch.get("parent_process_key", "")),
            }
            for branch in self.ctx.branches
        ]

        branch_refs_by_stage: dict[str, list[str]] = {}
        for branch in artifact_branches:
            parent = branch.get("parent_stage_ref")
            if parent:
                branch_refs_by_stage.setdefault(parent, []).append(branch["id"])

        for stage in artifact_stages:
            stage["branch_refs"] = branch_refs_by_stage.get(stage["id"], [])

        return {
            "schema_version": SCHEMA_VERSION,
            "artifact_id": str(uuid.uuid4()),
            "domain": {
                "name": scope.get("domain", "Untitled Domain"),
                "scope": scope.get("scope", ""),
                "target_user": scope.get("target_user", ""),
                "non_goals": list(scope.get("non_goals") or []),
            },
            "mental_model": {
                "summary": mental_model.get("summary", ""),
                "flow": list(mental_model.get("flow") or []),
            },
            "goals": [self._build_goal(goal) for goal in goals],
            "shared_foundations": artifact_foundations,
            "main_processes": artifact_processes,
            "stages": artifact_stages,
            "concepts": [self._build_concept(concept) for concept in concepts],
            "operations": [self._build_operation(operation) for operation in operations],
            "branches": artifact_branches,
            "practices": [self._build_practice(practice) for practice in self.ctx.practices],
            "expansion_map": [
                {
                    "title": item.get("title", ""),
                    "description": item.get("description", ""),
                    "from_goal_ref": self.goal_ids.get(item.get("from_goal_key") or ""),
                }
                for item in self.ctx.expansion_map
                if item.get("title")
            ],
            "metadata": {
                "language": self.ctx.settings.get("language", "auto"),
                "generator": GENERATOR,
                "source_ids": list(self.ctx.input.get("source_ids") or []),
            },
        }

    def _allocate(
        self,
        goals: list[dict[str, Any]],
        processes: list[dict[str, Any]],
        stages: list[dict[str, Any]],
        concepts: list[dict[str, Any]],
        operations: list[dict[str, Any]],
    ) -> None:
        for goal in goals:
            self.goal_ids[goal["key"]] = self.ids.allocate("goal", goal["title"])
        for process in processes:
            self.process_ids[process["key"]] = self.ids.allocate(
                "process",
                process["title"],
                suffix_parts=(self._goal_slug(process["goal_key"]),),
            )
        for stage in stages:
            self.stage_ids[stage["key"]] = self.ids.allocate(
                "stage",
                stage["title"],
                suffix_parts=(self._goal_slug(stage.get("goal_key", "")),),
            )
        for concept in concepts:
            self.concept_ids[concept["key"]] = self.ids.allocate("concept", concept["name"])
        for operation in operations:
            self.operation_ids[operation["key"]] = self.ids.allocate("operation", operation["name"])
        for branch in self.ctx.branches:
            self.branch_ids[branch["key"]] = self.ids.allocate("branch", branch["title"])
        for practice in self.ctx.practices:
            self.practice_ids[practice["key"]] = self.ids.allocate("practice", practice["title"])
        for foundation in self.ctx.foundations:
            self.foundation_ids[foundation["key"]] = self.ids.allocate(
                "foundation", foundation.get("title", "shared")
            )

    def _goal_slug(self, goal_key: str) -> str:
        allocated = self.goal_ids.get(goal_key, goal_key)
        return allocated.split(".", 1)[-1] if "." in allocated else goal_key

    def _build_goal(self, goal: dict[str, Any]) -> dict[str, Any]:
        return {
            "id": self.goal_ids[goal["key"]],
            "title": goal["title"],
            "outcome": goal["outcome"],
            "why_it_matters": goal.get("why_it_matters", ""),
            "prerequisite_goal_refs": [
                self.goal_ids[key]
                for key in goal.get("prerequisite_goal_keys", [])
                if key in self.goal_ids
            ],
            "evidence_refs": list(goal.get("evidence_refs") or []),
        }

    def _build_process(
        self,
        process: dict[str, Any],
        *,
        starts: dict[str, Any],
        stage_keys: list[str],
        stage_map: dict[str, dict[str, Any]],
        practice: dict[str, Any] | None,
    ) -> dict[str, Any]:
        start_type = starts.get("type", "zero")
        start_ref = starts.get("ref")
        return {
            "id": self.process_ids[process["key"]],
            "goal_ref": self.goal_ids[process["goal_key"]],
            "title": process["title"],
            "start": {
                "type": start_type,
                "ref": self.foundation_ids.get(start_ref) if start_ref else None,
            },
            "stage_refs": [self.stage_ids[key] for key in stage_keys if key in self.stage_ids],
            "outcome": process["outcome"],
            "practice_ref": self.practice_ids.get(practice["key"]) if practice else None,
        }

    def _build_stage(self, stage: dict[str, Any], binding: dict[str, Any]) -> dict[str, Any]:
        return {
            "id": self.stage_ids[stage["key"]],
            "title": stage["title"],
            "local_goal": stage["local_goal"],
            "why_it_exists": stage.get("why_it_exists", ""),
            "local_outcome": stage.get("local_outcome", ""),
            "concept_refs": [
                self.concept_ids[key]
                for key in binding.get("concept_keys", [])
                if key in self.concept_ids
            ],
            "operation_refs": [
                self.operation_ids[key]
                for key in binding.get("operation_keys", [])
                if key in self.operation_ids
            ],
            "branch_refs": [],
            "implementation_details": list(stage.get("implementation_details") or []),
            "example": stage.get("example"),
            "evidence_refs": list(stage.get("evidence_refs") or []),
        }

    def _build_concept(self, concept: dict[str, Any]) -> dict[str, Any]:
        return {
            "id": self.concept_ids[concept["key"]],
            "name": concept["name"],
            "definition": concept.get("definition", ""),
            "role": concept.get("role", ""),
            "related_concept_refs": [
                self.concept_ids[key]
                for key in concept.get("related_concept_keys", [])
                if key in self.concept_ids
            ],
            "key_operation_refs": [
                self.operation_ids[key]
                for key in concept.get("key_operation_keys", [])
                if key in self.operation_ids
            ],
        }

    def _build_operation(self, operation: dict[str, Any]) -> dict[str, Any]:
        return {
            "id": self.operation_ids[operation["key"]],
            "name": operation["name"],
            "definition": operation.get("definition", ""),
            "purpose": operation.get("purpose", ""),
            "acts_on_concept_refs": [
                self.concept_ids[key]
                for key in operation.get("acts_on_concept_keys", [])
                if key in self.concept_ids
            ],
            "common_failures": list(operation.get("common_failures") or []),
        }

    def _build_practice(self, practice: dict[str, Any]) -> dict[str, Any]:
        return {
            "id": self.practice_ids[practice["key"]],
            "title": practice["title"],
            "goal_ref": self.goal_ids.get(practice["process_key"].removeprefix("p_"), ""),
            "instructions": list(practice.get("instructions") or []),
            "expected_outcome": practice.get("expected_outcome", ""),
            "checkpoint_questions": list(practice.get("checkpoint_questions") or []),
        }


class AssembleStep:
    name = "H90"

    async def execute(self, ctx: HarnessContext, services: Any) -> StepResult:
        artifact = Assembler(ctx).assemble()
        return StepResult.success(
            {"artifact": artifact},
            events=[
                HarnessEvent(
                    "step.completed",
                    {
                        "step": self.name,
                        "goals": len(artifact["goals"]),
                        "processes": len(artifact["main_processes"]),
                        "stages": len(artifact["stages"]),
                    },
                )
            ],
            metrics={
                "goal_count": len(artifact["goals"]),
                "process_count": len(artifact["main_processes"]),
                "stage_count": len(artifact["stages"]),
            },
        )
