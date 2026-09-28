import type {
  Branch,
  Concept,
  COPArtifact,
  Goal,
  MainProcess,
  Operation,
  Practice,
  Stage,
} from "@cop-studio/cop-types";

function requireEntity<T extends { id: string }>(
  entities: T[],
  id: string,
  label: string,
): T {
  const value = entities.find((entity) => entity.id === id);
  if (!value) throw new Error(`${label} not found: ${id}`);
  return value;
}

export const artifactSelectors = {
  getGoal(artifact: COPArtifact, id: string): Goal {
    return requireEntity(artifact.goals, id, "Goal");
  },
  getProcess(artifact: COPArtifact, id: string): MainProcess {
    return requireEntity(artifact.main_processes, id, "MainProcess");
  },
  getStage(artifact: COPArtifact, id: string): Stage {
    return requireEntity(artifact.stages, id, "Stage");
  },
  getConcept(artifact: COPArtifact, id: string): Concept {
    return requireEntity(artifact.concepts, id, "Concept");
  },
  getOperation(artifact: COPArtifact, id: string): Operation {
    return requireEntity(artifact.operations, id, "Operation");
  },
  getProcessForGoal(artifact: COPArtifact, goalId: string): MainProcess {
    const process = artifact.main_processes.find((item) => item.goal_ref === goalId);
    if (!process) throw new Error(`MainProcess not found for Goal: ${goalId}`);
    return process;
  },
  getStagesForProcess(artifact: COPArtifact, process: MainProcess): Stage[] {
    return process.stage_refs.map((id) => this.getStage(artifact, id));
  },
  getConceptsForStage(artifact: COPArtifact, stage: Stage): Concept[] {
    return stage.concept_refs.map((id) => this.getConcept(artifact, id));
  },
  getOperationsForStage(artifact: COPArtifact, stage: Stage): Operation[] {
    return stage.operation_refs.map((id) => this.getOperation(artifact, id));
  },
  getBranchesForStage(artifact: COPArtifact, stage: Stage): Branch[] {
    return (stage.branch_refs ?? []).map((id) =>
      requireEntity(artifact.branches, id, "Branch"),
    );
  },
  getPracticeForProcess(
    artifact: COPArtifact,
    process: MainProcess,
  ): Practice | undefined {
    return process.practice_ref
      ? artifact.practices.find((item) => item.id === process.practice_ref)
      : undefined;
  },
};

