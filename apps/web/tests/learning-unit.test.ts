import type { COPArtifact } from "@cop-studio/cop-types";
import type { LearningUnit } from "@cop-studio/cop-types/learning-unit";
import { createElement } from "react";
import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it } from "vitest";

import artifactJSON from "../../../fixtures/langchain-basic-cop.json";
import unitJSON from "../../../fixtures/langchain-basic-learning-unit.json";
import manifest from "../../../fixtures/langchain-basic-learning-unit.manifest.json";
import { LearningUnitReader } from "../components/learning-unit-reader";
import { LearningOverview } from "../components/learning-overview";
import { learningUnitBinding, unitContentHash } from "../lib/learning-unit-binding";
import { exportObservation, newObservation, parseObservation } from "../lib/learning-observation";

const artifact = artifactJSON as COPArtifact;
const unit = unitJSON as LearningUnit;
const hash = manifest.unit_sha256;

describe("bound learning unit", () => {
  it("matches Python-generated hashes for both documents", () => {
    expect(unitContentHash(unit)).toBe(manifest.unit_sha256);
    expect(unitContentHash(artifact)).toBe(manifest.artifact_sha256);
    expect(learningUnitBinding(unit, artifact, manifest)).toBe(true);
  });
  it("rejects stale teaching, methods, or a failed/unknown check manifest", () => {
    expect(learningUnitBinding({ ...unit, outcome: "Different" }, artifact, manifest)).toBe(false);
    expect(learningUnitBinding(unit, { ...artifact, artifact_id: "changed-source" } as COPArtifact, manifest)).toBe(false);
    expect(learningUnitBinding(unit, artifact, { ...manifest, issues: [{ code: "GAP", ref: "x", message: "Gap" }] })).toBe(false);
    expect(learningUnitBinding(unit, artifact, { ...manifest, scope: "everything-verified" })).toBe(false);
    expect(learningUnitBinding(unit, artifact, { ...manifest, checker_version: "unknown" })).toBe(false);
  });
  it("does not depend on object key insertion order", () => {
    const reordered = Object.fromEntries(Object.entries(artifact).reverse());
    expect(unitContentHash(reordered)).toBe(unitContentHash(artifact));
    expect(unitContentHash([1, 2])).not.toBe(unitContentHash([2, 1]));
  });
  it("renders conceptual scaffolding before methods without changing source content", () => {
    const before = JSON.stringify({ unit, artifact });
    const html = renderToStaticMarkup(createElement(LearningUnitReader, { unit, artifact, unitHash: hash, bindingValid: true }));
    expect(html.indexOf("Understand the ideas")).toBeLessThan(html.indexOf("Follow the method"));
    expect(html).toContain("Partial goal");
    expect(html).toContain("not execution records");
    expect(html).toContain("not evidence of stable automatic generation");
    expect(html).toContain("Your observations · local only");
    expect(html).not.toContain("Mark complete");
    expect(JSON.stringify({ unit, artifact })).toBe(before);
  });
  it("fails closed rather than presenting methods from the wrong revision", () => {
    const html = renderToStaticMarkup(createElement(LearningUnitReader, { unit, artifact, unitHash: hash, bindingValid: false }));
    expect(html).toContain("Lesson revision mismatch");
    expect(html).not.toContain("Follow the method");
  });
  it("shows the saved overall explanation before asking for the first action", () => {
    const before = JSON.stringify(artifact);
    const html = renderToStaticMarkup(createElement(LearningOverview, {
      artifact, projectId: "p", versionId: "v", title: "A saved plan",
    }));
    expect(html.indexOf("How the ideas fit together")).toBeLessThan(html.indexOf("FIRST ACTION IN THE PLAN"));
    expect(html).toContain("not an independently verified account");
    expect(JSON.stringify(artifact)).toBe(before);
  });
});

describe("unverified local observations", () => {
  it("round-trips answers, observed results and support use without manufacturing a grade", () => {
    const record = newObservation(unit, hash);
    const firstPath = record.active_path_id;
    const question = unit.steps[0].practice;
    record.paths[firstPath].responses[question.id] = {
      answer: "My explanation", help_used: "Read the first hint", hints_revealed: 1, criteria_revealed: true,
    };
    record.paths[firstPath].observations[unit.steps[0].stage_ref] = "Observed a mismatch";
    const exported = exportObservation(record);
    const restored = parseObservation(exported, unit, hash);
    expect(restored.scope).toBe("unverified-self-report");
    expect(restored.paths).toEqual(record.paths);
    expect(exported).not.toContain("mastered");
    expect(exported).not.toContain("score");
    expect(Object.keys(restored.paths)).toHaveLength(unit.paths.length);
    expect(restored.paths[unit.paths[1].id].responses).toEqual({});
  });
  it.each(["unit_sha256", "artifact_sha256", "unit_id", "format", "scope"])("rejects changed %s instead of reattaching evidence", (field) => {
    const value = { ...newObservation(unit, hash), [field]: "changed" };
    expect(() => parseObservation(JSON.stringify(value), unit, hash)).toThrow();
  });
  it("rejects unknown paths, questions, stage ids, support counts and malformed values", () => {
    const valid = newObservation(unit, hash);
    const pathId = valid.active_path_id;
    const question = unit.steps[0].practice;
    const variants = [
      { ...valid, active_path_id: "unknown" },
      { ...valid, paths: {} },
      { ...valid, updated_at: "not a timestamp" },
      { ...valid, score: 100 },
      { ...valid, paths: { ...valid.paths, [pathId]: { responses: { unknown: {} }, observations: {} } } },
      { ...valid, paths: { ...valid.paths, [pathId]: { responses: {}, observations: { unknown: "x" } } } },
      ...[-1, 0.5, question.hints.length + 1].map((hints_revealed) => ({ ...valid, paths: { ...valid.paths, [pathId]: { observations: {}, responses: { [question.id]: { answer: "x", help_used: "", hints_revealed, criteria_revealed: false } } } } })),
      { ...valid, paths: { ...valid.paths, [pathId]: { observations: {}, responses: { [question.id]: { answer: 3, help_used: "", hints_revealed: 0, criteria_revealed: false } } } } },
    ];
    variants.forEach((value) => expect(() => parseObservation(JSON.stringify(value), unit, hash)).toThrow());
    expect(() => parseObservation("{broken", unit, hash)).toThrow();
    expect(() => parseObservation("x".repeat(200001), unit, hash)).toThrow();
  });
});
