import type { COPArtifact, Stage } from "@cop-studio/cop-types";

import { artifactSelectors } from "./artifact-selectors";

/** Read-only projection: no summarisation, inferred prerequisites, or API calls. */
export function learningGuide(artifact: COPArtifact) {
  const routes = artifact.goals.map((goal) => {
    const process = artifactSelectors.getProcessForGoal(artifact, goal.id);
    const stages = artifactSelectors.getStagesForProcess(artifact, process);
    const foundation = artifact.shared_foundations.find((item) => item.id === process.start.ref);
    return { goal, process, stages, foundation };
  });
  const firstRoute = routes[0];
  const firstId = firstRoute?.foundation?.stage_refs[0] ?? firstRoute?.stages[0]?.id;
  const firstStep = firstId ? artifactSelectors.getStage(artifact, firstId) : undefined;
  return { routes, firstStep, firstGoal: firstRoute?.goal };
}

/** Presence, not semantic correctness. A target outcome is NOT a validation. */
export function stepGuide(stage: Stage) {
  const details = stage.implementation_details ?? [];
  const actionable = details.filter((detail) => detail.action?.trim() || detail.command?.trim());
  const checks = details.flatMap((detail, index) => detail.expected_result?.trim()
    ? [{ index, title: detail.title, text: detail.expected_result }]
    : []);
  const cautions = details.flatMap((detail, index) => detail.caution?.trim()
    ? [{ index, title: detail.title, text: detail.caution }]
    : []);
  return {
    details,
    checks,
    cautions,
    hasInstructions: actionable.length > 0,
    hasCommands: details.some((detail) => detail.command?.trim()),
    uncheckedActions: actionable.filter((detail) => !detail.expected_result?.trim()).length,
  };
}

/** In Learn, a foundation is a real selectable step, not a jump to latest data. */
export function selectLearningStep({
  stages, foundations, selectedStageId, statusFor, foundationStatusFor,
}: {
  stages: Stage[];
  foundations: Stage[];
  selectedStageId?: string;
  statusFor: (id: string) => string;
  foundationStatusFor: (id: string) => string;
}) {
  const ordered = [...foundations, ...stages];
  const selected = ordered.find((stage) => stage.id === selectedStageId);
  const next = foundations.find((stage) => foundationStatusFor(stage.id) !== "completed")
    ?? stages.find((stage) => statusFor(stage.id) !== "completed");
  const stage = selected ?? next ?? stages[0] ?? foundations[0];
  return { stage, ordered, isFoundation: foundations.some((item) => item.id === stage?.id) };
}
