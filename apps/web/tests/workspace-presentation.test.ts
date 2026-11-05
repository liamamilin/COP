import type { COPArtifact } from "@cop-studio/cop-types";
import { renderToStaticMarkup } from "react-dom/server";
import { beforeEach, describe, expect, it, vi } from "vitest";

import reference from "../../../fixtures/reference-langchain-cop.json";
import OverviewPage from "../app/projects/[projectId]/page";
import ConceptPage from "../app/projects/[projectId]/concepts/[conceptId]/page";
import OperationPage from "../app/projects/[projectId]/operations/[operationId]/page";
import { ProjectShell } from "../components/project-shell";
import * as api from "../lib/api";
import type { ProjectSummary, VersionDetail } from "../lib/api";

vi.mock("next/navigation", () => ({ useRouter: () => ({ refresh: vi.fn() }) }));
vi.mock("../lib/api", async (original) => ({
  ...await original<typeof api>(),
  getProjectWorkspace: vi.fn(),
  getWorkspace: vi.fn(),
  getEffectiveGenerationSettings: vi.fn(),
}));

const project: ProjectSummary = {
  id: "p", title: "A concise project title", description: "", domain: "Topic", scope: "",
  preferred_language: "auto", status: "active", created_at: "", updated_at: "", latest_version: 1,
};
let artifact: COPArtifact;
let version: VersionDetail;

beforeEach(() => {
  artifact = structuredClone(reference) as COPArtifact;
  artifact.domain.name = "A generated paragraph is explanatory content, not a page title. ".repeat(30);
  version = {
    id: "v", project_id: project.id, version_number: 1, parent_version_id: null,
    run_id: null, change_summary: "", created_by: "user", created_at: "", artifact, evidence_sources: {},
  };
  vi.mocked(api.getProjectWorkspace).mockResolvedValue({ project, version, artifact, draft: null });
  vi.mocked(api.getWorkspace).mockResolvedValue({ project, version, artifact });
  vi.mocked(api.getEffectiveGenerationSettings).mockRejectedValue(new Error("Not needed for reading"));
});

describe("published workspace presentation", () => {
  it("owns a scoped style boundary and uses project identity in the topbar", () => {
    const html = renderToStaticMarkup(ProjectShell({
      project, version, artifact, active: "overview", children: "Reading content",
    }));
    expect(html).toContain('class="workspace published-workspace"');
    expect(html).toContain('class="workspace-project-name"');
    expect(html).toContain("v1");
    expect(html).not.toContain(artifact.domain.name);
    expect(html).toContain("Reading content");
  });

  it("shows an actionable overview and route before background and management", async () => {
    const html = renderToStaticMarkup(await OverviewPage({ params: Promise.resolve({ projectId: project.id }) }));
    expect(html).toContain(`<h1>${project.title}</h1>`);
    expect(html).toContain('href="/projects/p/learn?version=v"');
    expect(html).toContain('href="#learning-goals"');
    expect(html.indexOf('id="learning-goals"')).toBeLessThan(html.indexOf("MENTAL MODEL"));
    expect(html.indexOf('id="learning-goals"')).toBeLessThan(html.indexOf("MANAGE THIS COP"));
    for (const goal of artifact.goals) {
      expect(html).toContain(`/projects/p/goals/${encodeURIComponent(goal.id)}`);
    }
  });

  it("exposes the generated approach and preserves scope/exclusions without mutation", async () => {
    const before = JSON.stringify(artifact);
    const html = renderToStaticMarkup(await OverviewPage({ params: Promise.resolve({ projectId: project.id }) }));
    const context = html.slice(html.indexOf('<details class="workspace-context">'), html.indexOf("</details>"));
    expect(html).toContain(`<p class="learning-approach">${artifact.domain.name}</p>`);
    expect(context).toContain(artifact.domain.scope);
    expect(context).toContain("check this matches your intent");
    expect(context).toContain(artifact.domain.target_user);
    for (const exclusion of artifact.domain.non_goals ?? []) expect(context).toContain(exclusion);
    expect(html).toContain("Publishing saved this plan; it did not run its steps.");
    expect(JSON.stringify(artifact)).toBe(before);
  });

  it("renders concept roles as explanation, not display headings", async () => {
    const concept = artifact.concepts[0];
    const html = renderToStaticMarkup(await ConceptPage({ params: Promise.resolve({ projectId: "p", conceptId: concept.id }) }));
    expect(html).toContain("ROLE IN THE SYSTEM</p><p class=\"lead-copy\">");
    expect(html).not.toContain(`<h2>${concept.role}</h2>`);
  });

  it("renders operation purposes as explanation, not display headings", async () => {
    const operation = artifact.operations.find((item) => item.purpose)!;
    const html = renderToStaticMarkup(await OperationPage({ params: Promise.resolve({ projectId: "p", operationId: operation.id }) }));
    expect(html).toContain("PURPOSE</p><p class=\"lead-copy\">");
    expect(html).not.toContain(`<h2>${operation.purpose}</h2>`);
  });
});
