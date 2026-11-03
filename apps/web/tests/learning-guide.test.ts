import type { COPArtifact, Stage } from "@cop-studio/cop-types";
import { createElement } from "react";
import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it, vi } from "vitest";

import reference from "../../../fixtures/langchain-basic-cop.json";
import { learningGuide, selectLearningStep, stepGuide } from "../lib/learning-guide";
import { StageContent } from "../components/stage-content";
import { LearnView } from "../components/learn-view";
import { LearningOverview } from "../components/learning-overview";
import type { LearningProgress } from "../lib/api";

vi.mock("next/navigation", () => ({ useRouter: () => ({ refresh: vi.fn() }) }));
const artifact = reference as COPArtifact;
const route = learningGuide(artifact).routes[0];
const foundations = artifact.shared_foundations[0].stage_refs.map((id) => artifact.stages.find((s) => s.id === id)!);
const selection = {
  stages: route.stages, foundations,
  statusFor: () => "not_started", foundationStatusFor: () => "not_started",
};
const progress: LearningProgress = {
  project_id: "p", version_id: "frozen-v1", version_number: 1, completed_goals: 0, total_goals: 1,
  foundations: foundations.map((stage) => ({ stage_id: stage.id, status: "not_started", updated_at: null })),
  goals: [{ goal_id: route.goal.id, title: route.goal.title, completed: false, completed_stages: 0,
    total_stages: route.stages.length, blocked_by: [], practice: null,
    stages: route.stages.map((stage) => ({ stage_id: stage.id, status: "not_started", notes: null, updated_at: null })),
  }],
};
const minimal: Stage = {
  id: "reading", title: "Read a concept", local_goal: "Explain a distinction", local_outcome: "An explanation",
  concept_refs: [], operation_refs: [],
};
const renderStep = (stage: Stage) => renderToStaticMarkup(createElement(StageContent, { artifact, projectId: "p", stage, sources: {} }));

describe("read-only learning projections", () => {
  it("keeps canonical routes and starts at the relevant foundation without modifying content", () => {
    const before = JSON.stringify(artifact);
    const view = learningGuide(artifact);
    expect(view.routes.map((item) => item.goal.id)).toEqual(artifact.goals.map((g) => g.id));
    expect(view.routes[0].stages.map((s) => s.id)).toEqual(route.process.stage_refs);
    expect(view.firstStep?.id).toBe(foundations[0].id);
    expect(JSON.stringify(artifact)).toBe(before);
  });

  it("does not mistake an outcome or example for an observable check", () => {
    const stage = { ...minimal, example: { summary: "An example", output: "Example output" } };
    expect(stepGuide(stage).checks).toEqual([]);
    expect(stepGuide(stage).hasInstructions).toBe(false);
  });

  it("reports partially unchecked actions and ignores whitespace-only instructions", () => {
    const stage = { ...minimal, implementation_details: [
      { title: "A", action: "Do A", expected_result: "Observe A" },
      { title: "B", command: "check B" },
      { title: "C", action: "  ", expected_result: " " },
    ] };
    const guide = stepGuide(stage);
    expect(guide.checks.map((c) => c.text)).toEqual(["Observe A"]);
    expect(guide.uncheckedActions).toBe(1);
    expect(guide.hasCommands).toBe(true);
  });

  it("selects unfinished preparation before process steps, and respects explicit reading choices", () => {
    expect(selectLearningStep(selection).stage.id).toBe(foundations[0].id);
    expect(selectLearningStep({ ...selection, selectedStageId: route.stages[1].id }).stage.id).toBe(route.stages[1].id);
    expect(selectLearningStep({ ...selection, foundationStatusFor: () => "completed" }).stage.id).toBe(route.stages[0].id);
    expect(selectLearningStep({ ...selection, selectedStageId: "other-process-step" }).stage.id).toBe(foundations[0].id);
  });

  it("keeps completed steps explicitly reviewable and resolves only the current process preparation", () => {
    const selected = selectLearningStep({ ...selection, statusFor: () => "completed", foundationStatusFor: () => "completed", selectedStageId: foundations[1].id });
    expect(selected.stage.id).toBe(foundations[1].id);
    expect(selected.isFoundation).toBe(true);
    expect(selected.ordered.map((s) => s.id)).toEqual([...foundations, ...route.stages].map((s) => s.id));
    expect(selectLearningStep({ ...selection, foundations: [] }).stage.id).toBe(route.stages[0].id);
  });
});

describe("reader-facing content", () => {
  it("places method and checks before background without repeating purpose or output", () => {
    const stage = route.stages[0];
    const html = renderStep(stage);
    const instructions = html.indexOf('data-guide-section="instructions"');
    const checks = html.indexOf('data-guide-section="checks"');
    const background = html.indexOf('data-guide-section="background"');
    expect(instructions).toBeLessThan(checks);
    expect(checks).toBeLessThan(background);
    expect(html).toContain('<details class="step-reference"');
    expect(html).not.toContain('<details class="step-reference" open');
    expect(html).toContain("Completion is self-reported");
    expect(html.indexOf("Understand the ideas used here")).toBeLessThan(instructions);
    expect(html).toContain('class="step-primer" open');
    expect(html).toContain("Why it matters here");
  });

  it("shows previous planned output and next-step context without claiming a verified dependency", () => {
    const html = renderStep(route.stages[1]);
    expect(html).toContain("COMING FROM THE PREVIOUS STEP");
    expect(html).toContain(route.stages[0].title);
    expect(html).toContain("Where this leads");
    expect(html).toContain("not confirmation that it has been completed");
  });

  it("shows missing content honestly for older and conceptual steps without adding commands", () => {
    const html = renderStep(minimal);
    expect(html).toContain("No concrete instructions");
    expect(html).toContain("No explicit check");
    expect(html).not.toContain("Code / command");
    expect(html).not.toContain("Verified");
  });

  it("shows a coverage warning when only some actions have checks", () => {
    const html = renderStep({ ...minimal, implementation_details: [
      { title: "One", action: "Read the given text", expected_result: "Name the distinction" },
      { title: "Two", action: "Try another case" },
    ] });
    expect(html).toContain("Some actions have no explicit check");
  });

  it("escapes generated commands and never renders executable HTML", () => {
    const html = renderStep({ ...minimal, implementation_details: [{ title: "Inspect", command: '<script>alert("x")</script>' }] });
    expect(html).toContain("&lt;script&gt;");
    expect(html).not.toContain("<script>");
  });

  it("shows the chosen approach before the route and pins the first action to the version", () => {
    const html = renderToStaticMarkup(createElement(LearningOverview, { artifact, projectId: "p", versionId: "frozen-v1", title: "A tool" }));
    expect(html.indexOf("What this plan covers")).toBeLessThan(html.indexOf('id="learning-goals"'));
    expect(html).toContain("Publishing saved this plan; it did not run its steps.");
    expect(html).toContain(`version=frozen-v1&amp;goal=${route.goal.id}&amp;stage=${foundations[0].id}`);
    expect(html).toContain("Open first step");
  });

  it("keeps selected-step navigation within the frozen version and before progress controls", () => {
    const html = renderToStaticMarkup(createElement(LearnView, {
      artifact, projectId: "p", progress, selectedGoalId: route.goal.id, selectedStageId: route.stages[1].id, sources: {},
    }));
    const reader = html.slice(html.indexOf('id="current-step"'));
    expect(reader).toContain(route.stages[1].title);
    expect(reader.indexOf('data-guide-section="checks"')).toBeLessThan(reader.indexOf('class="learn-stage-navigation"'));
    expect(html).toContain(`version=frozen-v1&amp;stage=${route.stages[1].id}#current-step`);
    expect(html).not.toContain(`/projects/p/stages/${route.stages[1].id}`);
    expect(html).toContain('aria-current="step"');
  });
});
