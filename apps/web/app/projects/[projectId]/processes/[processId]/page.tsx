import { PracticeCard } from "../../../../../components/practice-card";
import { ProcessRail } from "../../../../../components/process-rail";
import { ProjectShell } from "../../../../../components/project-shell";
import { getWorkspace } from "../../../../../lib/api";
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

  return (
    <ProjectShell project={project} version={version} artifact={artifact} active="process">
      <div className="content-wrap narrow-content">
        <header className="page-header detail-header">
          <p className="eyebrow">MAIN PROCESS · {process.stage_refs.length} STAGES</p>
          <h1>{process.title}</h1>
          <p className="lead-copy">{goal.outcome}</p>
        </header>
        <ProcessRail artifact={artifact} process={process} projectId={projectId} />
        {practice && <PracticeCard practice={practice} />}
      </div>
    </ProjectShell>
  );
}

