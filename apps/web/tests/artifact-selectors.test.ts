import { describe, expect, it } from "vitest";
import type { COPArtifact } from "@cop-studio/cop-types";

import { artifactSelectors } from "../lib/artifact-selectors";

const artifact = {
  goals: [{ id: "goal.one", title: "Goal", outcome: "Done" }],
  main_processes: [
    {
      id: "process.one",
      goal_ref: "goal.one",
      title: "Process",
      start: { type: "zero" },
      stage_refs: ["stage.one"],
      outcome: "Done",
    },
  ],
  stages: [
    {
      id: "stage.one",
      title: "Stage",
      local_goal: "Do it",
      concept_refs: ["concept.one"],
      operation_refs: ["operation.one"],
    },
  ],
  concepts: [{ id: "concept.one", name: "Thing", definition: "A thing", role: "Core" }],
  operations: [{ id: "operation.one", name: "Do", definition: "Act" }],
} as COPArtifact;

describe("artifactSelectors", () => {
  it("keeps process ordering from stage_refs", () => {
    const process = artifactSelectors.getProcessForGoal(artifact, "goal.one");
    expect(artifactSelectors.getStagesForProcess(artifact, process)[0]?.id).toBe("stage.one");
  });

  it("fails loudly for broken references", () => {
    expect(() => artifactSelectors.getStage(artifact, "stage.missing")).toThrow(
      "Stage not found",
    );
  });
});

