import { ProjectShell } from "../../../../../components/project-shell";
import { StageContent } from "../../../../../components/stage-content";
import { StageContextNavigation, StageStepNavigation } from "../../../../../components/stage-navigation";
import { getWorkspace } from "../../../../../lib/api";
import { artifactSelectors } from "../../../../../lib/artifact-selectors";

export default async function StagePage({
  params,
}: {
  params: Promise<{ projectId: string; stageId: string }>;
}) {
  const { projectId, stageId } = await params;
  const { project, version, artifact } = await getWorkspace(projectId);
  const stage = artifactSelectors.getStage(artifact, decodeURIComponent(stageId));
  const context = artifactSelectors.getStageContext(artifact, stage);

  return (
    <ProjectShell project={project} version={version} artifact={artifact} active="stage">
      <div className="content-wrap stage-layout">
        <StageContextNavigation artifact={artifact} projectId={projectId} stage={stage} />

        <article className="stage-content">
          <header className="page-header detail-header">
            <p className="eyebrow">{context.kind === "foundation" ? "FOUNDATION" : "STAGE"} {context.index + 1}</p>
            <h1>{stage.title}</h1>
            <div className="local-goal-block">
              <span>LOCAL GOAL</span>
              <p>{stage.local_goal}</p>
            </div>
          </header>

          {stage.why_it_exists && (
            <section className="reading-section">
              <p className="eyebrow">WHY THIS EXISTS</p>
              <p className="lead-copy">{stage.why_it_exists}</p>
            </section>
          )}

          {/* Shared with Learn Mode. Two renderers of the same fields had already
              drifted: Learn showed the method, this page showed nothing. */}
          <StageContent
            artifact={artifact}
            projectId={projectId}
            sources={version.evidence_sources ?? {}}
            stage={stage}
          />

          {stage.local_outcome && (
            <section className="outcome-banner"><span>LOCAL OUTCOME</span><p>{stage.local_outcome}</p></section>
          )}

          <StageStepNavigation artifact={artifact} projectId={projectId} stage={stage} />
        </article>
      </div>
    </ProjectShell>
  );
}
