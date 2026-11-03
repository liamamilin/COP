import { createElement } from "react";
import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it } from "vitest";

import { ProjectCollection } from "../components/project-collection";
import type { ProjectSummary } from "../lib/api";
import { findProjects, projectPage, projectView, PROJECT_PAGE_SIZE } from "../lib/project-collection";

function projects(count: number): ProjectSummary[] {
  return Array.from({ length: count }, (_, index) => ({
    id: `p${index}`, title: `Project ${index + 1}`, description: "A description",
    domain: "A domain", scope: "A scope", preferred_language: "en", status: "active",
    created_at: new Date(Date.UTC(2026, 0, index + 1)).toISOString(),
    updated_at: new Date(Date.UTC(2026, 0, count - index)).toISOString(),
    latest_version: index % 2 ? null : 1,
  }));
}

describe("project collection browsing", () => {
  it("defaults to a richer small collection, a denser large one, and a list for archives", () => {
    expect(projectView(2, "auto")).toBe("overview");
    expect(projectView(30, "auto")).toBe("compact");
    expect(projectView(200, "auto", true)).toBe("list");
    expect(projectView(1, "compact")).toBe("compact");
    expect(projectView(200, "overview")).toBe("overview");
    expect(projectView(200, "list")).toBe("list");
  });

  it("searches the whole collection before paging, not only the visible twelve", () => {
    const all = projects(40);
    all[39].title = "传播学案例研究";
    const result = projectPage(findProjects(all, "传播学", "all", "updated"), 1);
    expect(result.total).toBe(1);
    expect(result.items[0].id).toBe("p39");
  });

  it("searches stored title, description, scope and domain without depending on optional previews", () => {
    const all = projects(4);
    all[0].title = "ＡＧＥＮＴ";
    all[1].description = "Rare description";
    all[2].scope = "Rare scope";
    all[3].domain = "Rare domain";
    expect(findProjects(all, " agent ", "all", "updated").map((p) => p.id)).toEqual(["p0"]);
    expect(findProjects(all, "RARE", "all", "updated")).toHaveLength(3);
    expect(findProjects(all, "<script>", "all", "updated")).toEqual([]);
  });

  it("sorts by actual update time, creation time or title, without mutating input", () => {
    const all = projects(12);
    const before = JSON.stringify(all);
    expect(findProjects(all, "", "all", "updated")[0].id).toBe("p0");
    expect(findProjects(all, "", "all", "created")[0].id).toBe("p11");
    expect(findProjects(all, "", "all", "title").slice(0, 3).map((p) => p.title)).toEqual(["Project 1", "Project 2", "Project 3"]);
    expect(JSON.stringify(all)).toBe(before);
  });

  it("combines publication filters with the query, not with an invented draft state", () => {
    const all = projects(30);
    expect(findProjects(all, "", "published", "updated")).toHaveLength(15);
    expect(findProjects(all, "Project 2", "unpublished", "updated").every((p) => p.latest_version === null)).toBe(true);
    expect(findProjects(all, "missing", "published", "updated")).toEqual([]);
  });

  it("bounds page size and clamps a stale page after the result count changes", () => {
    const all = projects(200);
    expect(projectPage(all, 1).items).toHaveLength(PROJECT_PAGE_SIZE);
    expect(projectPage(all, 2).items[0].id).toBe("p12");
    expect(projectPage(all, 100).page).toBe(17);
    expect(projectPage(all.slice(0, 2), 17)).toMatchObject({ page: 1, from: 1, to: 2, total: 2 });
    expect(projectPage([], 4)).toMatchObject({ page: 1, pageCount: 1, from: 0, to: 0, items: [] });
  });

  it("keeps stable input order when timestamps are missing rather than guessing activity", () => {
    const all = projects(3).map((p) => ({ ...p, updated_at: "", created_at: "invalid" }));
    expect(findProjects(all, "", "all", "updated")).toEqual(all);
    expect(findProjects(all, "", "all", "created")).toEqual(all);
  });

  it("renders at most a page of a large library, not two hundred large outlines", () => {
    const html = renderToStaticMarkup(createElement(ProjectCollection, { projects: projects(200) }));
    expect(html).toContain('data-view="compact"');
    expect(html.match(/data-project-row/g)).toHaveLength(PROJECT_PAGE_SIZE);
    expect(html).toContain("Search projects");
    expect(html).toContain("1–12 of 200 projects");
    expect(html).toContain("Next page");
    expect(html).not.toContain("Learning path");
    expect(html).not.toContain("percent complete");
  });
});
