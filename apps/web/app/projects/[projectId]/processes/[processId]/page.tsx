import { PracticeRecorder } from "../../../../../components/practice-recorder";
import { ProcessRail } from "../../../../../components/process-rail";
import { ProjectShell } from "../../../../../components/project-shell";
import { getLearningProgress, getWorkspace } from "../../../../../lib/api";
import { artifactSelectors } from "../../../../../lib/artifact-selectors";

export default async function ProcessPage({
  params,
}: {
  params: Promise<{ projectId: string; processId: string }>;
}) {
  const { projectId, processId } = await params;
  const { project, version, artifact } = await getWorkspace(projectId);
  const process = artifactSelectors.getProcess(artifact, decodeURIComponent(processId));
  const goal = artifactSelectors.getGoal(artifact, process.goal_ref);
  const practice = artifactSelectors.getPracticeForProcess(artifact, process);
  const goalProgress = (
    await getLearningProgress(projectId, version.id).catch(() => null)
  )?.goals.find((item) => item.goal_id === goal.id);

  return (
    <ProjectShell project={project} version={version} artifact={artifact} active="process">
      <div className="content-wrap narrow-content">
        <header className="page-header detail-header">
          <p className="eyebrow">MAIN PROCESS · {process.stage_refs.length} STAGES</p>
          <h1>{process.title}</h1>
          <p className="lead-copy">{goal.outcome}</p>
        </header>
        <ProcessRail artifact={artifact} process={process} projectId={projectId} />
        {practice && (
          <PracticeRecorder
            goalId={goal.id}
            practice={practice}
            progress={goalProgress?.practice ?? null}
            projectId={projectId}
            versionId={version.id}
          />
        )}
      </div>
    </ProjectShell>
  );
}
