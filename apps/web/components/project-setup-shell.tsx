import Link from "next/link";
import type { ReactNode } from "react";

import type { ProjectSummary } from "../lib/api";

export function ProjectSetupShell({
  project,
  active,
  children,
}: {
  project: ProjectSummary;
  active: "overview" | "sources" | "settings";
  children: ReactNode;
}) {
  const root = `/projects/${project.id}`;
  return (
    <div className="workspace setup-workspace">
      <aside className="project-sidebar">
        <div className="project-identity">
          <span className="sidebar-kicker">DRAFT PROJECT</span>
          <h2>{project.title}</h2>
          <span className="draft-state"><i /> No COP generated</span>
        </div>
        <nav aria-label="Project setup navigation">
          <Link className={active === "overview" ? "active" : ""} href={root}><span>01</span> Overview</Link>
          <Link className={active === "sources" ? "active" : ""} href={`${root}/sources`}><span>02</span> Sources</Link>
          <Link className={active === "settings" ? "active" : ""} href={`${root}/settings`}><span>03</span> Project settings</Link>
        </nav>
        <div className="sidebar-footer"><span>Setup mode</span><span>{project.preferred_language}</span></div>
      </aside>
      <main className="workspace-main">
        <div className="workspace-topbar"><Link href="/">All projects</Link><div><span>{project.domain}</span><span className="topbar-separator">/</span><strong>Draft</strong></div></div>
        {children}
      </main>
    </div>
  );
}

