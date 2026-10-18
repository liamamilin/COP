import Link from "next/link";

import { getArchivedProjects, getProjects, type ProjectSummary } from "../lib/api";

/**
 * The library.
 *
 * Active and archived are counted separately and shown separately. Hiding an
 * archived project without saying where it went is how a user concludes the app
 * lost their work, and spec `18` requires a project list that survives a restart
 * -- which it does, but only visibly.
 */
export default async function HomePage() {
  let active: ProjectSummary[] = [];
  let archived: ProjectSummary[] = [];
  let unavailable = false;
  try {
    [active, archived] = await Promise.all([getProjects(), getArchivedProjects()]);
  } catch {
    unavailable = true;
  }

  return (
    <main className="home-shell">
      <section className="home-hero">
        <p className="eyebrow">STRUCTURE BEFORE DETAIL</p>
        <h1>
          把知识变成一条
          <br />
          可以走通的主线。
        </h1>
        <p className="hero-copy">
          COP Studio 将领域压缩为目标、主流程、阶段，以及真正影响行动的概念与操作。
        </p>
      </section>

      <section className="project-section" aria-labelledby="projects-heading">
        <div className="section-heading">
          <div>
            <p className="eyebrow">YOUR LIBRARY</p>
            <h2 id="projects-heading">知识项目</h2>
          </div>
          <div className="home-actions">
            <span className="count-label">
              {active.length} active
              {archived.length > 0 ? ` · ${archived.length} archived` : ""}
            </span>
            <Link className="primary-link" href="/projects/new">
              New COP ↗
            </Link>
          </div>
        </div>

        {unavailable ? (
          <div className="empty-state error-state">
            <span className="status-dot" />
            <div>
              <h3>API 尚未连接</h3>
              <p>启动 FastAPI 与 PostgreSQL 后，这里会显示已发布的 COP。</p>
            </div>
          </div>
        ) : active.length === 0 ? (
          <div className="empty-state">
            <div className="empty-glyph">→</div>
            <div>
              <h3>还没有 COP</h3>
              <p>从一个目标开始，或运行 seed 命令导入参考项目。</p>
            </div>
            <Link className="primary-link" href="/projects/new">
              Create COP
            </Link>
          </div>
        ) : (
          <div className="project-grid">
            {active.map((project) => (
              <Link className="project-card" href={`/projects/${project.id}`} key={project.id}>
                <div className="project-card-top">
                  <span className="project-monogram">{project.title.slice(0, 1)}</span>
                  <span className="version-pill">v{project.latest_version ?? "—"}</span>
                </div>
                <h3>{project.title}</h3>
                <p>{project.scope}</p>
                <div className="project-card-footer">
                  <span>{project.preferred_language.toUpperCase()}</span>
                  <span>
                    Open workspace <b>↗</b>
                  </span>
                </div>
              </Link>
            ))}
          </div>
        )}

        {archived.length > 0 && (
          <details className="archived-projects">
            <summary>
              {archived.length} archived project{archived.length === 1 ? "" : "s"}
            </summary>
            <p className="muted-note">
              Archived projects keep every source, version, and learning record. Restore one to
              bring it back.
            </p>
            <ul>
              {archived.map((project) => (
                <li key={project.id}>
                  <div>
                    <strong>{project.title}</strong>
                    <small>
                      {project.scope || "No scope recorded"} · v
                      {project.latest_version ?? "—"}
                    </small>
                  </div>
                  <Link className="secondary-button" href={`/projects/${project.id}`}>
                    Open ↗
                  </Link>
                </li>
              ))}
            </ul>
          </details>
        )}
      </section>
    </main>
  );
}
