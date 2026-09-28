import Link from "next/link";

import { PracticeCard } from "../../../../../components/practice-card";
import { ProcessRail } from "../../../../../components/process-rail";
import { ProjectShell } from "../../../../../components/project-shell";
import { getWorkspace } from "../../../../../lib/api";
import { artifactSelectors } from "../../../../../lib/artifact-selectors";

export default async function GoalPage({
  params,
}: {
  params: Promise<{ projectId: string; goalId: string }>;
}) {
  const { projectId, goalId } = await params;
  const { project, version, artifact } = await getWorkspace(projectId);
  const goal = artifactSelectors.getGoal(artifact, decodeURIComponent(goalId));
  const process = artifactSelectors.getProcessForGoal(artifact, goal.id);
  const practice = artifactSelectors.getPracticeForProcess(artifact, process);

  return (
    <ProjectShell project={project} version={version} artifact={artifact} active="goal">
      <div className="content-wrap narrow-content">
        <header className="page-header detail-header">
          <p className="eyebrow">GOAL · CAPABILITY OUTCOME</p>
          <h1>{goal.title}</h1>
          <p className="lead-copy">{goal.outcome}</p>
          {goal.why_it_matters && <div className="why-line"><span>WHY IT MATTERS</span>{goal.why_it_matters}</div>}
        </header>

        <div className="process-title-row">
          <div>
            <p className="eyebrow">MAIN PROCESS</p>
            <h2>{process.title}</h2>
          </div>
          <Link href={`/projects/${projectId}/processes/${encodeURIComponent(process.id)}`}>
            Focus process ↗
          </Link>
        </div>
        <ProcessRail artifact={artifact} process={process} projectId={projectId} />
        {practice && <PracticeCard practice={practice} />}
      </div>
    </ProjectShell>
  );
}

