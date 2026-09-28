import Link from "next/link";

import { getProjects, type ProjectSummary } from "../lib/api";

export default async function HomePage() {
  let projects: ProjectSummary[] = [];
  let unavailable = false;
  try {
    projects = await getProjects();
  } catch {
    unavailable = true;
  }

  return (
    <main className="home-shell">
      <section className="home-hero">
        <p className="eyebrow">STRUCTURE BEFORE DETAIL</p>
        <h1>把知识变成一条<br />可以走通的主线。</h1>
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
            <span className="count-label">{projects.length} COP</span>
            <Link className="primary-link" href="/projects/new">New COP ↗</Link>
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
        ) : projects.length === 0 ? (
          <div className="empty-state">
            <div className="empty-glyph">→</div>
            <div>
              <h3>还没有 COP</h3>
              <p>从一个目标开始，或运行 seed 命令导入参考项目。</p>
            </div>
            <Link className="primary-link" href="/projects/new">Create COP</Link>
          </div>
        ) : (
          <div className="project-grid">
            {projects.map((project) => (
              <Link className="project-card" href={`/projects/${project.id}`} key={project.id}>
                <div className="project-card-top">
                  <span className="project-monogram">{project.title.slice(0, 1)}</span>
                  <span className="version-pill">v{project.latest_version ?? "—"}</span>
                </div>
                <h3>{project.title}</h3>
                <p>{project.scope}</p>
                <div className="project-card-footer">
                  <span>{project.preferred_language.toUpperCase()}</span>
                  <span>Open workspace <b>↗</b></span>
                </div>
              </Link>
            ))}
          </div>
        )}
      </section>
    </main>
  );
}
