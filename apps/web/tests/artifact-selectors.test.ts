import { describe, expect, it } from "vitest";
import type { COPArtifact } from "@cop-studio/cop-types";
import { createElement } from "react";
import { renderToStaticMarkup } from "react-dom/server";

import { artifactSelectors } from "../lib/artifact-selectors";
import { ProcessRail } from "../components/process-rail";

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

  it("renders a 200-stage main process without quadratic lookup cost", () => {
    const stages = Array.from({ length: 200 }, (_, index) => ({
      id: `stage.${index}`,
      title: `Stage ${index}`,
      local_goal: `Complete step ${index}`,
      concept_refs: [`concept.${index}`],
      operation_refs: [`operation.${index}`],
    }));
    const large = {
      ...artifact,
      main_processes: [
        { ...artifact.main_processes[0], stage_refs: stages.map((stage) => stage.id) },
      ],
      stages,
      concepts: stages.map((_, index) => ({
        id: `concept.${index}`,
        name: `Concept ${index}`,
        definition: "Definition",
        role: "Core",
      })),
      operations: stages.map((_, index) => ({
        id: `operation.${index}`,
        name: `Operation ${index}`,
        definition: "Definition",
      })),
    } as COPArtifact;

    const started = performance.now();
    const html = renderToStaticMarkup(
      createElement(ProcessRail, {
        artifact: large,
        process: large.main_processes[0],
        projectId: "project",
      }),
    );

    expect(html).toContain("Stage 199");
    expect((html.match(/class=\"process-step\"/g) ?? []).length).toBe(201);
    expect(performance.now() - started).toBeLessThan(2_000);
  });
});
