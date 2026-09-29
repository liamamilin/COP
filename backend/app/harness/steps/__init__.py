"""Harness step registry.

The order here is the pipeline order and is the single source of truth for both
the runner and the progress UI. `H120` and `H130` are the validation tail; they
never call the provider directly.
"""

from app.harness.context import HarnessStep
from app.harness.steps.h00_intake import IntakeStep
from app.harness.steps.h10_scope import ScopeStep
from app.harness.steps.h20_research_brief import ResearchBriefStep
from app.harness.steps.h30_goals import GoalExtractionStep
from app.harness.steps.h40_processes import ProcessBuildStep
from app.harness.steps.h50_stages import StageEnrichmentStep
from app.harness.steps.h60_canonicalize import CanonicalizeStep
from app.harness.steps.h70_compression import CompressionStep
from app.harness.steps.h80_learning import LearningLayerStep
from app.harness.steps.h90_assemble import AssembleStep
from app.harness.steps.h100_critic import CriticStep
from app.harness.steps.h110_refine import RefineStep
from app.harness.steps.h120_validate import ValidateRepairStep
from app.harness.steps.h130_finalize import FinalizeStep
from app.harness.steps.h140_refine_target import RefineTargetStep

# Progress labels shown in the generation UI. Phases describe the user-visible
# stage of work, not the internal step name.
STEP_PIPELINE: tuple[HarnessStep, ...] = (
    IntakeStep(),
    ScopeStep(),
    ResearchBriefStep(),
    GoalExtractionStep(),
    ProcessBuildStep(),
    StageEnrichmentStep(),
    CanonicalizeStep(),
    CompressionStep(),
    LearningLayerStep(),
    AssembleStep(),
    CriticStep(),
    RefineStep(),
    ValidateRepairStep(),
    FinalizeStep(),
)

STEP_LABELS: dict[str, str] = {
    "H00": "Collecting the request",
    "H10": "Defining scope",
    "H20": "Understanding sources",
    "H30": "Finding high-value goals",
    "H40": "Building main processes",
    "H50": "Enriching stages",
    "H60": "Extracting concepts and operations",
    "H70": "Compressing shared foundations",
    "H80": "Generating learning material",
    "H90": "Assembling the artifact",
    "H100": "Reviewing quality",
    "H110": "Applying corrections",
    "H120": "Validating structure",
    "H130": "Finalizing candidate",
    "H140": "Proposing a refinement",
}

# A targeted run does not rebuild the COP. It reviews what already exists, then
# proposes a patch for one entity, so the pipeline here is deliberately short and
# ends at a proposal rather than at a candidate artifact.
TARGETED_PIPELINE: tuple[HarnessStep, ...] = (
    CriticStep(),
    RefineTargetStep(),
)

# Phases the user watches, in order. Several steps collapse into one phase so the
# progress list stays short enough to scan.
PHASES: tuple[tuple[str, str, tuple[str, ...]], ...] = (
    ("scope", "Defining scope", ("H00", "H10")),
    ("sources", "Understanding sources", ("H20",)),
    ("goals", "Finding high-value goals", ("H30",)),
    ("processes", "Building main processes", ("H40", "H50")),
    ("concepts", "Extracting concepts and operations", ("H60",)),
    ("compression", "Compressing shared foundations", ("H70",)),
    ("learning", "Generating learning material", ("H80",)),
    ("assembly", "Assembling the artifact", ("H90",)),
    ("quality", "Reviewing quality", ("H100", "H110")),
    ("finalize", "Finalizing artifact", ("H120", "H130")),
)

# Phases for a targeted refinement. Two, because that is all the work there is:
# review what exists, then propose a change.
TARGETED_PHASES: tuple[tuple[str, str, tuple[str, ...]], ...] = (
    ("quality", "Reviewing this entity", ("H100",)),
    ("refine", "Proposing a refinement", ("H140",)),
)

STEP_TO_PHASE: dict[str, str] = {step: phase for phase, _label, steps in PHASES for step in steps}

__all__ = [
    "PHASES",
    "STEP_LABELS",
    "STEP_PIPELINE",
    "STEP_TO_PHASE",
]
