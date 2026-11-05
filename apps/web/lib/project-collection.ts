import type { ProjectSummary } from "./api";

export type ProjectView = "auto" | "overview" | "compact" | "list";
export type ProjectSort = "updated" | "created" | "title";
export type ProjectFilter = "all" | "published" | "unpublished";
export const PROJECT_PAGE_SIZE = 12;

/** Defaults are density hints, not fixed column counts or a user preference. */
export function projectView(count: number, preference: ProjectView, archived = false) {
  return preference !== "auto" ? preference : archived ? "list" : count <= 4 ? "overview" : "compact";
}

function normalized(text: string) { return text.normalize("NFKC").toLocaleLowerCase(); }
function timestamp(text: string) {
  const value = Date.parse(text);
  return Number.isFinite(value) ? value : 0;
}

/** Whole supplied collection, before pagination. Never changes server-owned data. */
export function findProjects(projects: ProjectSummary[], query: string, filter: ProjectFilter, sort: ProjectSort) {
  const needle = normalized(query.trim());
  return projects.filter((project) => {
    if (filter === "published" && project.latest_version === null) return false;
    if (filter === "unpublished" && project.latest_version !== null) return false;
    return !needle || [project.title, project.description, project.domain, project.scope]
      .some((text) => normalized(text || "").includes(needle));
  }).sort((a, b) => sort === "title"
    ? a.title.localeCompare(b.title, undefined, { numeric: true, sensitivity: "base" })
    : timestamp(sort === "created" ? b.created_at : b.updated_at)
      - timestamp(sort === "created" ? a.created_at : a.updated_at));
}

export function projectPage(projects: ProjectSummary[], requested: number) {
  const total = projects.length;
  const pageCount = Math.max(1, Math.ceil(total / PROJECT_PAGE_SIZE));
  const page = Math.max(1, Math.min(Math.trunc(requested) || 1, pageCount));
  const offset = (page - 1) * PROJECT_PAGE_SIZE;
  return {
    items: projects.slice(offset, offset + PROJECT_PAGE_SIZE), page, pageCount, total,
    from: total ? offset + 1 : 0, to: Math.min(offset + PROJECT_PAGE_SIZE, total),
  };
}
