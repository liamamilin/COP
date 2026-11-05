import type { COPArtifact } from "@cop-studio/cop-types";
import { createElement } from "react";
import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it } from "vitest";

import reference from "../../../fixtures/reference-langchain-cop.json";
import { DraftReview } from "../components/draft-review";
import { draftReview } from "../lib/draft-review";

const artifact = reference as COPArtifact;

describe("draft review projection", () => {
  it("follows the existing goal, process and stage order without mutating the draft", () => {
    const before = JSON.stringify(artifact);
    const view = draftReview(artifact);
    expect(view.goals.map((g) => g.goal.id)).toEqual(artifact.goals.map((g) => g.id));
    for (const group of view.goals) {
      for (const route of group.processes) {
        expect(route.process.goal_ref).toBe(group.goal.id);
        expect(route.stages.map((s) => s.id)).toEqual(route.process.stage_refs);
      }
    }
    expect(JSON.stringify(artifact)).toBe(before);
  });

  it("keeps shared prerequisites and practice attached to the correct route", () => {
    const view = draftReview(artifact);
    expect(view.foundations.length).toBe(artifact.shared_foundations.length);
    for (const group of view.foundations) {
      expect(group.stages.map((s) => s.id)).toEqual(group.foundation.stage_refs);
    }
    for (const group of view.goals) for (const route of group.processes) {
      expect(route.practice?.id).toBe(route.process.practice_ref);
    }
  });

  it("renders reading content with explicit draft editing links, not published links", () => {
    const html = renderToStaticMarkup(createElement(DraftReview, { artifact, projectId: "p" }));
    expect(html).toContain("Your learning path");
    expect(html).toContain("Edit this step");
    expect(html).toContain("Check your understanding");
    expect(html).toContain(`/projects/p/draft/goals/${artifact.goals[0].id}`);
    expect(html).not.toContain('/projects/p/stages/');
    expect(html).not.toContain("draft-entity-id");
  });
});
