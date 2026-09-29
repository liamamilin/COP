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

interface ArtifactIndex {
  entities: Map<string, { id: string }>;
  processByGoal: Map<string, MainProcess>;
}

const indexes = new WeakMap<COPArtifact, ArtifactIndex>();

function indexFor(artifact: COPArtifact): ArtifactIndex {
  const cached = indexes.get(artifact);
  if (cached) return cached;
  const collections: ReadonlyArray<ReadonlyArray<{ id: string }>> = [
    artifact.goals,
    artifact.main_processes,
    artifact.stages,
    artifact.concepts,
    artifact.operations,
    artifact.branches ?? [],
    artifact.practices ?? [],
  ];
  const index: ArtifactIndex = {
    entities: new Map(collections.flat().map((entity) => [entity.id, entity])),
    processByGoal: new Map(artifact.main_processes.map((item) => [item.goal_ref, item])),
  };
  indexes.set(artifact, index);
  return index;
}

function requireEntity<T extends { id: string }>(
  artifact: COPArtifact,
  id: string,
  label: string,
): T {
  const value = indexFor(artifact).entities.get(id) as T | undefined;
  if (!value) throw new Error(`${label} not found: ${id}`);
  return value;
}

export const artifactSelectors = {
  getGoal(artifact: COPArtifact, id: string): Goal {
    return requireEntity(artifact, id, "Goal");
  },
  getProcess(artifact: COPArtifact, id: string): MainProcess {
    return requireEntity(artifact, id, "MainProcess");
  },
  getStage(artifact: COPArtifact, id: string): Stage {
    return requireEntity(artifact, id, "Stage");
  },
  getConcept(artifact: COPArtifact, id: string): Concept {
    return requireEntity(artifact, id, "Concept");
  },
  getOperation(artifact: COPArtifact, id: string): Operation {
    return requireEntity(artifact, id, "Operation");
  },
  getProcessForGoal(artifact: COPArtifact, goalId: string): MainProcess {
    const process = indexFor(artifact).processByGoal.get(goalId);
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
      requireEntity(artifact, id, "Branch"),
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
