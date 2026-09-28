import type { COPArtifact } from "@cop-studio/cop-types";
import Link from "next/link";
import type { ReactNode } from "react";

import type { ProjectSummary, VersionDetail } from "../lib/api";

interface ProjectShellProps {
  project: ProjectSummary;
  version: VersionDetail;
  artifact: COPArtifact;
  active:
    | "overview"
    | "goal"
    | "process"
    | "stage"
    | "concept"
    | "operation"
    | "sources"
    | "settings";
  children: ReactNode;
}

export function ProjectShell({
  project,
  version,
  artifact,
  active,
  children,
}: ProjectShellProps) {
  const projectPath = `/projects/${project.id}`;
  return (
    <div className="workspace">
      <aside className="project-sidebar">
        <div className="project-identity">
          <span className="sidebar-kicker">CURRENT COP</span>
          <h2>{project.title}</h2>
          <span className="published-state"><i /> Published v{version.version_number}</span>
        </div>

        <nav aria-label="Project navigation">
          <Link className={active === "overview" ? "active" : ""} href={projectPath}>
            <span>01</span> Overview
          </Link>
          <p className="nav-label">GOALS</p>
          {artifact.goals.map((goal, index) => (
            <Link
              className={active === "goal" ? "subtle-active" : ""}
              href={`${projectPath}/goals/${encodeURIComponent(goal.id)}`}
              key={goal.id}
            >
              <span>{String(index + 1).padStart(2, "0")}</span> {goal.title}
            </Link>
          ))}
          <p className="nav-label">EXPLORE</p>
          <Link className={active === "sources" ? "active" : ""} href={`${projectPath}/sources`}>
            <span>↳</span> Sources
          </Link>
          <Link className={active === "settings" ? "active" : ""} href={`${projectPath}/settings`}>
            <span>↳</span> Project settings
          </Link>
          <div className="nav-stats">
            <span>{artifact.concepts.length} concepts</span>
            <span>{artifact.operations.length} operations</span>
          </div>
        </nav>

        <div className="sidebar-footer">
          <span>Schema {artifact.schema_version}</span>
          <span>{artifact.metadata.language ?? "auto"}</span>
        </div>
      </aside>

      <main className="workspace-main">
        <div className="workspace-topbar">
          <Link href="/">All projects</Link>
          <div>
            <span>{artifact.domain.name}</span>
            <span className="topbar-separator">/</span>
            <strong>{version.created_by}</strong>
          </div>
        </div>
        {children}
      </main>
    </div>
  );
}
