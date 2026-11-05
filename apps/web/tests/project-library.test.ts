import { renderToStaticMarkup } from "react-dom/server";
import { beforeEach, describe, expect, it, vi } from "vitest";

import HomePage from "../app/page";
import { ProjectLibrary } from "../components/project-library";
import * as api from "../lib/api";
import type { ProjectSummary } from "../lib/api";
import { projectPreview } from "../lib/project-preview";
import reference from "../../../fixtures/langchain-basic-cop.json";
import type { COPArtifact } from "@cop-studio/cop-types";

vi.mock("../lib/api", async (original) => ({
  ...await original<typeof api>(), getProjects: vi.fn(), getArchivedProjects: vi.fn(), getLatestVersion: vi.fn(),
}));
const project: ProjectSummary = {
  id: "p", title: "自用工具", description: "A project description", domain: "A tool", scope: "Build a personal tool",
  preferred_language: "zh-CN", status: "active", created_at: "", updated_at: "", latest_version: 1,
};
beforeEach(() => {
  vi.mocked(api.getProjects).mockResolvedValue([project]);
  vi.mocked(api.getArchivedProjects).mockResolvedValue([]);
  vi.mocked(api.getLatestVersion).mockRejectedValue(new Error("Preview unavailable"));
});

describe("project library presentation", () => {
  it("is a compact library with project and creation links, not a marketing hero", () => {
    const html = renderToStaticMarkup(ProjectLibrary({ active: [project], archived: [] }));
    expect(html).toContain("<h1>Projects</h1>");
    expect(html).toContain('href="/projects/new"');
    expect(html).toContain('href="/projects/p"');
    expect(html).toContain("Published · v1");
    expect(html).toContain(project.scope);
    expect(html).not.toContain("home-hero");
    expect(html).not.toContain("STRUCTURE BEFORE DETAIL");
    expect(html).not.toContain("project-monogram");
  });

  it("does not present an unpublished project as a published version or a known draft", () => {
    const html = renderToStaticMarkup(ProjectLibrary({ active: [{ ...project, latest_version: null }], archived: [] }));
    expect(html).toContain("Not published");
    expect(html).not.toContain("Published ·");
    expect(html).not.toContain("Draft ready");
  });

  it("keeps archived work reachable but separate and collapsed by default", () => {
    const archived = { ...project, id: "archived", status: "archived" as const };
    const html = renderToStaticMarkup(ProjectLibrary({ active: [project], archived: [archived] }));
    expect(html).toContain("Archived projects");
    expect(html).toContain('href="/projects/archived"');
    expect(html.indexOf('href="/projects/p"')).toBeLessThan(html.indexOf("Archived projects"));
    expect(html).not.toContain(" open=");
  });

  it("offers an understandable empty state without seed commands or technical setup", () => {
    const html = renderToStaticMarkup(ProjectLibrary({ active: [], archived: [] }));
    expect(html).toContain("Create your first project");
    expect(html).not.toContain("seed");
    expect(html).not.toContain("PostgreSQL");
  });

  it("separates unavailable data from an empty library", () => {
    const html = renderToStaticMarkup(ProjectLibrary({ active: [], archived: [], unavailable: true }));
    expect(html).toContain('role="alert"');
    expect(html).toContain("temporarily unavailable");
    expect(html).toContain("Reload library");
    expect(html).not.toContain("Create your first project");
  });

  it("preserves project text and order, safely escaping markup", () => {
    const active = [{ ...project, title: "<script>Title</script>", scope: "A long scope ".repeat(100) }, { ...project, id: "second" }];
    const before = JSON.stringify(active);
    const html = renderToStaticMarkup(ProjectLibrary({ active, archived: [] }));
    expect(html).toContain("&lt;script&gt;Title&lt;/script&gt;");
    expect(html).not.toContain("<script>");
    expect(html).toContain(active[0].scope);
    expect(html.indexOf('href="/projects/p"')).toBeLessThan(html.indexOf('href="/projects/second"'));
    expect(JSON.stringify(active)).toBe(before);
  });

  it("keeps fetching outside the presentation component and retains both read paths", async () => {
    const html = renderToStaticMarkup(await HomePage());
    expect(api.getProjects).toHaveBeenCalledOnce();
    expect(api.getArchivedProjects).toHaveBeenCalledOnce();
    expect(html).toContain(project.title);
  });

  it("renders a connection failure without failing the page", async () => {
    vi.mocked(api.getProjects).mockRejectedValue(new Error("Offline"));
    expect(renderToStaticMarkup(await HomePage())).toContain("temporarily unavailable");
  });

  it("shows a bounded route preview and real counts, not the whole syllabus or invented progress", () => {
    const artifact = reference as COPArtifact;
    const before = JSON.stringify(artifact);
    const preview = projectPreview(artifact);
    const html = renderToStaticMarkup(ProjectLibrary({ active: [project], archived: [], previews: { p: preview } }));
    expect(html).toContain(artifact.goals[0].title);
    for (const goal of artifact.goals.slice(0, 3)) expect(html).toContain(goal.title);
    for (const goal of artifact.goals.slice(3)) expect(html).not.toContain(goal.title);
    expect(html).toContain("Learning path");
    expect(html).toContain(`${artifact.goals.length} goals · ${artifact.stages.length} steps`);
    expect(html).not.toContain("Open workspace");
    expect(html).not.toContain("Open a project to continue.");
    expect(preview.stepCount).toBe(artifact.stages.length);
    expect(html).not.toContain("percent complete");
    expect(JSON.stringify(artifact)).toBe(before);
  });

  it("keeps lifecycle controls outside the project navigation link", () => {
    const html = renderToStaticMarkup(ProjectLibrary({ active: [project], archived: [] }));
    const endOfLink = html.indexOf("</a>", html.indexOf('aria-label="Open project:'));
    expect(endOfLink).toBeLessThan(html.indexOf('data-project-actions="p"'));
    expect(html).toContain('aria-label="Actions for 自用工具"');
    expect(html).toContain('aria-expanded="false"');
    expect(html).not.toContain("Archive</button>");
    expect(html).not.toContain("Delete</button>");
    expect(html).not.toContain("Confirm delete");
  });
});
