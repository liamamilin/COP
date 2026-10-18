import { readFileSync } from "node:fs";
import { createElement } from "react";
import { renderToStaticMarkup } from "react-dom/server";
import type { COPArtifact } from "@cop-studio/cop-types";
import { describe, expect, it, vi } from "vitest";

import { artifactSelectors } from "../lib/artifact-selectors";
import { StageContent } from "../components/stage-content";
import { StageContextNavigation, StageStepNavigation } from "../components/stage-navigation";
import { LearnView } from "../components/learn-view";
import BasicPrototypePage from "../app/prototypes/langchain-basic/page";
import type { LearningProgress } from "../lib/api";

vi.mock("next/navigation", () => ({ useRouter: () => ({ refresh: vi.fn() }) }));

const artifact = JSON.parse(readFileSync(
  new URL("../../../fixtures/langchain-basic-cop.json", import.meta.url), "utf8",
)) as COPArtifact;
const projectId = "basic-prototype";

function navigation(stageId: string, input = artifact) {
  return renderToStaticMarkup(createElement(StageStepNavigation, {
    artifact: input, projectId, stage: artifactSelectors.getStage(input, stageId),
  }));
}

describe("Basic COP navigation and content", () => {
  it("renders a read-only prototype with resolvable local references, not fake project links", () => {
    const html = renderToStaticMarkup(createElement(BasicPrototypePage));
    expect(html).toContain("NOT PUBLISHED");
    expect(html).toContain("准备独立 Python 环境");
    expect(html).toContain('id="prototype-practice"');
    expect(html).toContain('href="#source-basic-agents-docs"');
    expect(html).toContain('id="source-basic-agents-docs"');
    expect(html).toContain('href="#operation-operation.foundation.install"');
    expect(html).toContain('id="operation-operation.foundation.install"');
    expect(html).not.toContain("/projects//");
    expect(html).not.toContain("Mark complete");
  });
  it("orders foundation setup and config and continues into the dependent process", () => {
    const setup = artifactSelectors.getStage(artifact, "stage.foundation.install");
    expect(artifactSelectors.getStageContext(artifact, setup).kind).toBe("foundation");
    expect(navigation(setup.id)).toContain("Next: 显式配置 key、endpoint、model");
    const config = navigation("stage.foundation.model");
    expect(config).toContain("Previous: 准备独立 Python 环境");
    expect(config).toContain("/stages/stage.basic.create-agent");
    expect(config).toContain("Continue:");
  });

  it("keeps every foundation stage reachable from a regular stage", () => {
    const html = renderToStaticMarkup(createElement(StageContextNavigation, {
      artifact, projectId, stage: artifactSelectors.getStage(artifact, "stage.basic.invoke"),
    }));
    for (const id of ["stage.foundation.install", "stage.foundation.model", "stage.basic.create-agent", "stage.basic.invoke", "stage.basic.inspect"]) {
      expect(html).toContain(`/stages/${id}`);
    }
    expect(html).toContain('aria-current="step"');
    expect(navigation("stage.basic.create-agent")).toContain("/stages/stage.foundation.model");
    expect(navigation("stage.basic.inspect")).toContain("Open process and practice");
    expect(navigation("stage.basic.inspect")).toContain("/processes/process.basic");
  });

  it("offers a choice when a foundation feeds multiple processes instead of selecting one", () => {
    const multiple = structuredClone(artifact);
    multiple.main_processes.push({ ...multiple.main_processes[0], id: "process.tools", title: "Tools process" });
    const html = navigation("stage.foundation.model", multiple);
    expect(html).toContain("CHOOSE A PROCESS");
    expect(html).toContain("/processes/process.basic");
    expect(html).toContain("/processes/process.tools");
    expect(html).not.toContain("/stages/stage.basic.create-agent");
  });

  it("renders actual executable code, explicit input rules and optional initialization", () => {
    const html = renderToStaticMarkup(createElement(StageContent, {
      artifact, projectId, stage: artifactSelectors.getStage(artifact, "stage.basic.create-agent"), sources: {},
    }));
    expect(html).toContain("Code / command");
    expect(html).toContain("def build_agent(settings: Settings)");
    expect(html).toContain("api_key=settings.api_key");
    expect(html).toContain("base_url=settings.base_url");
    expect(html).toContain("BRANCHES · OPTIONAL PATHS");
    expect(html).toContain("--model-init identifier");
    expect(html).toContain("Show full code");
    expect(html).toContain("先理解文件中的核心，而不是全部 CLI");
    expect(html).toContain("Unresolved source:"); // No invented source readiness.
  });

  it("opens foundation content inside Learn's selected artifact version without a latest-version jump", () => {
    const progress: LearningProgress = {
      project_id: projectId, version_id: "old-published-version", version_number: 1,
      completed_goals: 0, total_goals: 1,
      foundations: artifact.shared_foundations[0].stage_refs.map((stage_id) => ({ stage_id, status: "not_started", updated_at: null })),
      goals: [{ goal_id: "goal.basic", title: "Basic", completed: false, completed_stages: 0,
        total_stages: 3, blocked_by: [], practice: null,
        stages: artifact.main_processes[0].stage_refs.map((stage_id) => ({ stage_id, status: "not_started", notes: null, updated_at: null })),
      }],
    };
    const html = renderToStaticMarkup(createElement(LearnView, {
      artifact, projectId, progress, selectedGoalId: "goal.basic", sources: {},
    }));
    expect(html).toContain("Open foundation: 显式配置 key、endpoint、model");
    expect(html).toContain("def load_settings(");
    expect(html).toContain("LC_BASE_URL");
    expect(html).toContain("Outcome:");
    expect(html).toContain("version=old-published-version");
    // Read-only disclosure, not a navigation to the latest Stage/Workspace.
    expect(html).not.toContain("/stages/stage.foundation.model");
  });
});
