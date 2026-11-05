import type { COPArtifact } from "@cop-studio/cop-types";

export interface ProjectPreview {
  summary: string;
  goals: { id: string; title: string }[];
  stepCount: number;
}

/** No fetching or generated summaries: display the saved plan's actual route. */
export function projectPreview(artifact: COPArtifact): ProjectPreview {
  return {
    summary: artifact.domain.name,
    goals: artifact.goals.map(({ id, title }) => ({ id, title })),
    stepCount: artifact.stages.length,
  };
}
