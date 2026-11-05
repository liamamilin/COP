import type { COPArtifact } from "@cop-studio/cop-types";
import type { LearningUnit } from "@cop-studio/cop-types/learning-unit";
import { createElement } from "react";
import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it } from "vitest";

import artifactJSON from "../../../fixtures/communication-basics-cop.json";
import lessonJSON from "../../../fixtures/communication-basics-learning-unit.json";
import manifest from "../../../fixtures/communication-basics-learning-unit.manifest.json";
import { LearningUnitReader } from "../components/learning-unit-reader";
import { ReasoningWalkthrough } from "../components/teaching-explanation";
import { learningUnitBinding } from "../lib/learning-unit-binding";
import { newObservation, parseObservation, exportObservation } from "../lib/learning-observation";

const unit = lessonJSON as LearningUnit;
const artifact = artifactJSON as COPArtifact;

describe("reasoning-first lesson presentation", () => {
  it("shows the problem, case facts and unknowns before the method", () => {
    const before = JSON.stringify({ unit, artifact });
    const html = renderToStaticMarkup(createElement(LearningUnitReader, {
      unit, artifact, unitHash: manifest.unit_sha256,
      bindingValid: learningUnitBinding(unit, artifact, manifest),
    }));
    expect(html).not.toContain("Lesson revision mismatch");
    expect(html).toContain(unit.orientation!.question);
    expect(html).toContain(unit.orientation!.case_unknowns[0]);
    expect(html.indexOf("Why this learning route?")).toBeLessThan(html.indexOf("Follow the method"));
    expect(html.indexOf("Work through the reasoning")).toBeLessThan(html.indexOf("Follow the method"));
    expect(html).toContain(unit.steps[0].reasoning![0].limitation);
    expect(html).toContain("What it does not establish");
    expect(html).not.toContain("Code / command");
    expect(html).not.toContain("Mark complete");
    expect(JSON.stringify({ unit, artifact })).toBe(before);
  });

  it("does not manufacture a reasoning walkthrough when old content has none", () => {
    const html = renderToStaticMarkup(createElement(ReasoningWalkthrough, { moves: [], sources: [] }));
    expect(html).toBe("");
  });

  it("keeps notes tied to the precise unit and rejects an unrelated lesson", () => {
    const record = newObservation(unit, manifest.unit_sha256);
    const path = record.active_path_id;
    record.paths[path].responses[unit.steps[0].practice.id] = {
      answer: "This interpretation still needs evidence.", help_used: "One hint",
      hints_revealed: 1, criteria_revealed: false,
    };
    const exported = exportObservation(record);
    expect(parseObservation(exported, unit, manifest.unit_sha256).paths).toEqual(record.paths);
    expect(() => parseObservation(exported, { ...unit, unit_id: "another" }, manifest.unit_sha256)).toThrow();
    expect(() => parseObservation(exported, unit, "different-revision")).toThrow();
  });
});
