"""Harness execution context and step contracts.

The context is the single mutable carrier of Harness progress. It is serialized
into `generation_runs.checkpoint_json` after every major step so a retry can
resume from the last successful checkpoint instead of restarting at H00.
"""

import json
from dataclasses import asdict, dataclass, field
from enum import StrEnum
from typing import Any, Protocol

from app.core.errors import HarnessError


class StepStatus(StrEnum):
    SUCCESS = "success"
    PARTIAL_SUCCESS = "partial_success"
    RETRYABLE_FAILURE = "retryable_failure"
    FATAL_FAILURE = "fatal_failure"


TERMINAL_STEP_STATUSES = {StepStatus.SUCCESS, StepStatus.PARTIAL_SUCCESS}


@dataclass
class HarnessEvent:
    event_type: str
    payload: dict[str, Any] = field(default_factory=dict)


@dataclass
class StepResult:
    """Outcome of one Harness step.

    A step never mutates a published COP version. It only returns a checkpoint
    patch, which the runner decides whether to persist.
    """

    status: StepStatus
    checkpoint_patch: dict[str, Any] = field(default_factory=dict)
    events: list[HarnessEvent] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    metrics: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def success(
        cls,
        checkpoint_patch: dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> "StepResult":
        return cls(
            status=StepStatus.SUCCESS,
            checkpoint_patch=checkpoint_patch or {},
            **kwargs,
        )

    @classmethod
    def fatal(cls, code: str, message: str, **kwargs: Any) -> "StepResult":
        return cls(
            status=StepStatus.FATAL_FAILURE,
            events=[HarnessEvent("step.failed", {"code": code, "message": message})],
            **kwargs,
        )

    @classmethod
    def retryable(cls, code: str, message: str, **kwargs: Any) -> "StepResult":
        return cls(
            status=StepStatus.RETRYABLE_FAILURE,
            events=[HarnessEvent("step.retry_scheduled", {"code": code, "message": message})],
            **kwargs,
        )


@dataclass
class HarnessContext:
    run_id: str
    project_id: str
    base_version_id: str | None = None
    input: dict[str, Any] = field(default_factory=dict)
    settings: dict[str, Any] = field(default_factory=dict)
    source_bundle: list[dict[str, Any]] = field(default_factory=list)

    scope_result: dict[str, Any] | None = None
    research_brief: dict[str, Any] | None = None
    intake: dict[str, Any] | None = None
    goals: list[dict[str, Any]] = field(default_factory=list)
    process_drafts: list[dict[str, Any]] = field(default_factory=list)
    stage_drafts: list[dict[str, Any]] = field(default_factory=list)
    concepts: list[dict[str, Any]] = field(default_factory=list)
    operations: list[dict[str, Any]] = field(default_factory=list)
    stage_bindings: dict[str, dict[str, list[str]]] = field(default_factory=dict)
    bound_stage_keys: list[str] = field(default_factory=list)
    branches: list[dict[str, Any]] = field(default_factory=list)
    foundations: list[dict[str, Any]] = field(default_factory=list)
    process_starts: dict[str, dict[str, Any]] = field(default_factory=dict)
    process_stage_keys: dict[str, list[str]] = field(default_factory=dict)
    mental_model: dict[str, Any] | None = None
    practices: list[dict[str, Any]] = field(default_factory=list)
    expansion_map: list[dict[str, Any]] = field(default_factory=list)
    critic_report: dict[str, Any] | None = None
    artifact: dict[str, Any] | None = None

    # Paths the user has edited by hand. H110 must never rewrite these.
    locked_paths: list[str] = field(default_factory=list)
    # Non-empty when the run regenerates one entity instead of a full COP.
    partial_target: dict[str, str] | None = None

    def apply(self, patch: dict[str, Any]) -> None:
        """Apply a checkpoint patch, ignoring keys that are not context fields."""
        valid = {key for key in self.__dataclass_fields__}
        for key, value in patch.items():
            if key in valid:
                setattr(self, key, value)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "HarnessContext":
        valid = {key for key in cls.__dataclass_fields__}
        return cls(**{key: value for key, value in data.items() if key in valid})

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False, sort_keys=True)

    def completed_checkpoints(self) -> list[str]:
        """Checkpoint keys already persisted, in pipeline order."""
        order = (
            ("scope", self.scope_result is not None),
            ("research_brief", self.research_brief is not None),
            ("goals", bool(self.goals)),
            ("processes", bool(self.process_drafts)),
            ("stages", bool(self.stage_drafts)),
            ("cop_core", bool(self.concepts) and bool(self.operations)),
            ("compression", bool(self.foundations) or bool(self.branches)),
            ("learning_layer", self.mental_model is not None),
            ("critic", self.critic_report is not None),
            ("artifact", self.artifact is not None),
        )
        return [name for name, present in order if present]

    def require(self, key: str) -> Any:
        value = getattr(self, key, None)
        if value is None:
            raise HarnessError(
                "HARNESS_CHECKPOINT_MISSING",
                f"Checkpoint '{key}' is required but was not produced",
            )
        return value


class HarnessServices(Protocol):
    """Capabilities a step may use. The runner supplies the implementation."""

    async def complete_structured(
        self, *, system_prompt: str, user_prompt: str, schema: dict[str, Any]
    ) -> dict[str, Any]: ...

    async def complete_text(self, *, system_prompt: str, user_prompt: str) -> str: ...

    def emit(self, event: HarnessEvent) -> None: ...

    def is_cancelled(self) -> bool: ...


class HarnessStep(Protocol):
    name: str

    async def execute(self, ctx: HarnessContext, services: HarnessServices) -> StepResult: ...
