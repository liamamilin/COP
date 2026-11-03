import Link from "next/link";

import type { ProjectSummary } from "../lib/api";
import type { ProjectPreview } from "../lib/project-preview";
import { ProjectCollection } from "./project-collection";

import styles from "./project-library.module.css";

/** Library presentation. Fetching and lifecycle interactions stay elsewhere. */
export function ProjectLibrary({ active, archived, previews = {}, unavailable = false }: {
  active: ProjectSummary[];
  archived: ProjectSummary[];
  previews?: Record<string, ProjectPreview>;
  unavailable?: boolean;
}) {
  return (
    <main className={styles.library}>
      <header className={styles.header}>
        <div>
          <h1>Projects</h1>
        </div>
        <Link className={styles.newProject} href="/projects/new"><span aria-hidden="true">+</span> New project</Link>
      </header>

      <section className={styles.projects} aria-labelledby="projects-heading">
        {(unavailable || active.length === 0) && <div className={styles.sectionHeading}>
          <h2 id="projects-heading">Active projects {!unavailable && <span>{active.length}</span>}</h2>
        </div>}

        {unavailable ? (
          <div className={styles.empty} role="alert">
            <h3>Projects are temporarily unavailable</h3>
            <p>We couldn&apos;t load your library. Check the API connection, then reload this page.</p>
            <Link className={styles.textLink} href="/">Reload library →</Link>
          </div>
        ) : active.length === 0 ? (
          <div className={styles.empty}>
            <h3>A place for your next learning project</h3>
            <p>Start with a topic or source material. Review the generated plan before you publish it.</p>
            <Link className={styles.textLink} href="/projects/new">Create your first project →</Link>
          </div>
        ) : (
          <ProjectCollection projects={active} previews={previews} heading={<h2 id="projects-heading">Active projects <span>{active.length}</span></h2>} />
        )}
      </section>

      {!unavailable && archived.length > 0 && (
        <details className={styles.archive}>
          <summary>Archived projects <span>{archived.length}</span></summary>
          <ProjectCollection projects={archived} archived />
        </details>
      )}

    </main>
  );
}
