import type { COPArtifact } from "@cop-studio/cop-types";

import { artifactSelectors } from "./artifact-selectors";

/** Read-only projection. The draft stays canonical; the review follows its routes. */
export function draftReview(artifact: COPArtifact) {
  return {
    foundations: artifact.shared_foundations.map((foundation) => ({
      foundation,
      stages: foundation.stage_refs.map((id) => artifactSelectors.getStage(artifact, id)),
    })),
    goals: artifact.goals.map((goal) => ({
      goal,
      processes: artifact.main_processes.filter((process) => process.goal_ref === goal.id)
        .map((process) => ({
          process,
          stages: artifactSelectors.getStagesForProcess(artifact, process),
          practice: artifactSelectors.getPracticeForProcess(artifact, process),
        })),
    })),
  };
}
