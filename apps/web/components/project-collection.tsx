"use client";

import Link from "next/link";
import { useId, useRef, useState, type ReactNode } from "react";

import type { ProjectSummary } from "../lib/api";
import {
  findProjects, projectPage, projectView,
  type ProjectFilter, type ProjectSort, type ProjectView,
} from "../lib/project-collection";
import type { ProjectPreview } from "../lib/project-preview";
import { ProjectActions } from "./project-actions";

import styles from "./project-library.module.css";

/** Collection browsing only. No fetching, lifecycle calls, or learning state. */
export function ProjectCollection({ projects, previews = {}, archived = false, heading }: {
  projects: ProjectSummary[]; previews?: Record<string, ProjectPreview>;
  archived?: boolean; heading?: ReactNode;
}) {
  const [preference, setPreference] = useState<ProjectView>("auto");
  const [query, setQuery] = useState("");
  const [filter, setFilter] = useState<ProjectFilter>("all");
  const [sort, setSort] = useState<ProjectSort>("updated");
  const [pageNumber, setPageNumber] = useState(1);
  const list = useRef<HTMLUListElement>(null);
  const id = useId();
  const view = projectView(projects.length, preference, archived);
  const results = projectPage(findProjects(projects, query, filter, sort), pageNumber);
  // Keep tools available while searching, even when the result set becomes small.
  const showFind = projects.length > 4 || !!query || filter !== "all";

  function resetSearch() { setQuery(""); setFilter("all"); setPageNumber(1); }
  function navigate(page: number) { setPageNumber(page); list.current?.focus(); }

  return <div className={styles.collection} data-project-collection data-view={view}>
    <div className={styles.collectionHeading}>
      {heading}
      <label className={styles.viewControl}>View
        <select aria-label={archived ? "Archived project view" : "Project view"} value={preference} onChange={(event) => setPreference(event.target.value as ProjectView)}>
          <option value="auto">Auto</option><option value="overview">Overview</option>
          <option value="compact">Compact</option><option value="list">List</option>
        </select>
      </label>
    </div>
    {showFind && <div className={styles.findTools}>
      <input type="search" aria-label={archived ? "Search archived projects" : "Search projects"} placeholder="Search projects…" value={query} onChange={(event) => { setQuery(event.target.value); setPageNumber(1); }} />
      <label>Status<select aria-label={archived ? "Archived publication status" : "Publication status"} value={filter} onChange={(event) => { setFilter(event.target.value as ProjectFilter); setPageNumber(1); }}>
        <option value="all">All</option><option value="published">Published</option><option value="unpublished">Not published</option>
      </select></label>
      <label>Sort<select aria-label={archived ? "Sort archived projects" : "Sort projects"} value={sort} onChange={(event) => { setSort(event.target.value as ProjectSort); setPageNumber(1); }}>
        <option value="updated">Recently updated</option><option value="created">Newest created</option><option value="title">Title</option>
      </select></label>
    </div>}
    {showFind && <p className={styles.resultCount} role="status">{results.total ? `${results.from}–${results.to} of ${results.total} projects` : "No matching projects"}</p>}
    {results.total ? <ul id={`${id}-projects`} ref={list} tabIndex={-1} className={styles.projectGrid} aria-label={archived ? "Archived projects" : "Active projects"}>
      {results.items.map((project) => {
        const preview = previews[project.id];
        return <li className={styles.projectCard} key={project.id} data-project-row>
          <Link className={styles.projectLink} href={`/projects/${project.id}`} aria-label={`${archived ? "Open archived project" : "Open project"}: ${project.title}`}>
            <p className={styles.cardStatus}>{project.latest_version === null ? "Not published" : `Published · v${project.latest_version}`}</p>
            <h3 title={project.title}>{project.title}</h3>
            <p className={styles.cardScope}>{(preview?.summary !== project.title ? preview?.summary : "") || project.scope || project.description || "Open this project to review its learning plan."}</p>
            {view === "overview" && preview?.goals[0] && <div className={styles.startPreview}>
              <span>Learning path</span>
              <ol>{preview.goals.slice(0, 3).map((goal, index) => <li key={goal.id}>
                <span aria-hidden="true">{String(index + 1).padStart(2, "0")}</span><span title={goal.title}>{goal.title}</span>
              </li>)}</ol>
            </div>}
            <div className={styles.cardFooter}>
              <span>{preview ? `${preview.goals.length} goals · ${preview.stepCount} steps` : "Open project"}</span>
              <span className={styles.projectArrow} aria-hidden="true">↗</span>
            </div>
          </Link>
          <ProjectActions projectId={project.id} title={project.title} archived={archived} />
        </li>;
      })}
    </ul> : <div className={styles.noMatches}><p>Try another title, topic, or publication status.</p><button type="button" onClick={resetSearch}>Clear filters</button></div>}
    {results.pageCount > 1 && <nav className={styles.pagination} aria-label={archived ? "Archived project pages" : "Project pages"}>
      <span>Page {results.page} of {results.pageCount}</span>
      <button type="button" aria-controls={`${id}-projects`} disabled={results.page === 1} onClick={() => navigate(results.page - 1)}>Previous page</button>
      <button type="button" aria-controls={`${id}-projects`} disabled={results.page === results.pageCount} onClick={() => navigate(results.page + 1)}>Next page</button>
    </nav>}
  </div>;
}
