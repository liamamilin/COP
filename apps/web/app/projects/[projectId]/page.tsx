import Link from "next/link";

import { GenerationSection } from "../../../components/generation-section";
import { ProjectSetupShell } from "../../../components/project-setup-shell";
import { ProjectShell } from "../../../components/project-shell";
import {
  getProjectSources,
  getProjectWorkspace,
} from "../../../lib/api";
import { artifactSelectors } from "../../../lib/artifact-selectors";

export default async function ProjectOverviewPage({
  params,
}: {
  params: Promise<{ projectId: string }>;
}) {
  const { projectId } = await params;
  const { project, version, draft } = await getProjectWorkspace(projectId);
  if (!version) {
    const sources = await getProjectSources(projectId);
    return (
      <ProjectSetupShell project={project} active="overview">
        <div className="content-wrap setup-overview">
          <header className="page-header detail-header">
            <p className="eyebrow">PROJECT READY · NO COP YET</p>
            <h1>{project.title}</h1>
            <p className="lead-copy">
              {project.scope || "Define the source material and scope for this COP."}
            </p>
          </header>

          <section className="setup-next-step">
            <span className="step-orbit">{sources.length}</span>
            <div>
              <p className="eyebrow">SOURCES</p>
              <h2>{sources.length ? "Review your sources" : "Add source material"}</h2>
              <p>
                {sources.length
                  ? `Your ${sources.length} extracted source(s) are ready. Generation can also work from the topic alone.`
                  : "Paste text, upload TXT/Markdown/PDF, or fetch a public URL. Sources are optional."}
              </p>
            </div>
            <Link className="primary-link" href={`/projects/${projectId}/sources`}>
              {sources.length ? "Open sources" : "Add sources"} ↗
            </Link>
          </section>

          <GenerationSection
            depth="standard"
            learnerLevel="new"
            projectId={projectId}
            scopeHint={project.scope}
            sourceIds={sources.map((source) => source.id)}
            topic={project.domain}
          />
        </div>
      </ProjectSetupShell>
    );
  }
  const artifact = version.artifact;

  return (
    <ProjectShell
      project={project}
      version={version}
      artifact={artifact}
      active="overview"
      hasDraft={draft !== null}
    >
      <div className="content-wrap">
        <header className="page-header overview-header">
          <div>
            <p className="eyebrow">DOMAIN OVERVIEW</p>
            <h1>{artifact.domain.name}</h1>
            <p>{artifact.domain.scope}</p>
          </div>
          <div className="artifact-metrics">
            <span><b>{artifact.goals.length}</b> Goals</span>
            <span><b>{artifact.main_processes.length}</b> Processes</span>
            <span><b>{artifact.stages.length}</b> Stages</span>
          </div>
        </header>

        <section className="mental-model-card">
          <div className="section-number">01</div>
          <div>
            <p className="eyebrow">MENTAL MODEL</p>
            <h2>How the system moves</h2>
            <p className="lead-copy">{artifact.mental_model.summary}</p>
            <div className="flow-strip">
              {(artifact.mental_model.flow ?? []).map((item, index) => (
                <div className="flow-item" key={`${item}-${index}`}>
                  <span>{String(index + 1).padStart(2, "0")}</span>
                  <strong>{item}</strong>
                </div>
              ))}
            </div>
          </div>
        </section>

        <section className="goal-map">
          <div className="section-title-row">
            <div>
              <p className="eyebrow">GOAL MAP</p>
              <h2>Capabilities worth building</h2>
            </div>
            <p>从可验证结果进入主流程，而不是从术语列表开始。</p>
          </div>
          <div className="goal-list">
            {artifact.goals.map((goal, index) => {
              const process = artifactSelectors.getProcessForGoal(artifact, goal.id);
              return (
                <Link
                  className="goal-row"
                  href={`/projects/${projectId}/goals/${encodeURIComponent(goal.id)}`}
                  key={goal.id}
                >
                  <span className="goal-number">{String(index + 1).padStart(2, "0")}</span>
                  <div>
                    <small>{process.stage_refs.length} STAGES</small>
                    <h3>{goal.title}</h3>
                    <p>{goal.outcome}</p>
                  </div>
                  <span className="goal-enter">Enter process <b>↗</b></span>
                </Link>
              );
            })}
          </div>
        </section>

        {artifact.shared_foundations.map((foundation) => (
          <section className="foundation-card" key={foundation.id}>
            <div>
              <p className="eyebrow">SHARED FOUNDATION</p>
              <h2>{foundation.title}</h2>
              <p>Repeated setup appears once, while every Main Process remains traceable to zero.</p>
            </div>
            <div className="foundation-stages">
              {foundation.stage_refs.map((stageId, index) => {
                const stage = artifactSelectors.getStage(artifact, stageId);
                return (
                  <Link href={`/projects/${projectId}/stages/${encodeURIComponent(stage.id)}`} key={stage.id}>
                    <span>{index + 1}</span>{stage.title}
                  </Link>
                );
              })}
            </div>
          </section>
        ))}
      </div>
    </ProjectShell>
  );
}
