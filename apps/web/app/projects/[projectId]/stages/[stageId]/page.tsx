import { ProjectShell } from "../../../../../components/project-shell";
import { StageContent } from "../../../../../components/stage-content";
import { StageContextNavigation, StageStepNavigation } from "../../../../../components/stage-navigation";
import { getWorkspace } from "../../../../../lib/api";
import { artifactSelectors } from "../../../../../lib/artifact-selectors";
import Link from "next/link";

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
          <nav className="step-breadcrumb" aria-label="Breadcrumb">
            <Link href={`/projects/${projectId}`}>Overview</Link><span>/</span>
            {context.process ? <Link href={`/projects/${projectId}/goals/${encodeURIComponent(context.process.goal_ref)}`}>{context.title}</Link> : <span>{context.title}</span>}
          </nav>
          <header className="page-header detail-header">
            <p className="eyebrow">{context.kind === "foundation" ? "PREPARATION" : "STEP"} {context.index + 1} OF {context.stages.length}</p>
            <h1>{stage.title}</h1>
          </header>

          {/* Shared with Learn Mode. Two renderers of the same fields had already
              drifted: Learn showed the method, this page showed nothing. */}
          <StageContent
            artifact={artifact}
            projectId={projectId}
            sources={version.evidence_sources ?? {}}
            stage={stage}
          />

          <StageStepNavigation artifact={artifact} projectId={projectId} stage={stage} />
        </article>
      </div>
    </ProjectShell>
  );
}
