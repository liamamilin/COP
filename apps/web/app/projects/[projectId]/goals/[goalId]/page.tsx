import Link from "next/link";

import { EvidencePanel } from "../../../../../components/evidence-panel";
import { PracticeRecorder } from "../../../../../components/practice-recorder";
import { ProcessRail } from "../../../../../components/process-rail";
import { ProjectShell } from "../../../../../components/project-shell";
import { getLearningProgress, getWorkspace } from "../../../../../lib/api";
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
  // Progress for this Goal, so the Practice card can show its real status. Read
  // here rather than in the client component so the first paint is correct; a
  // Practice that renders as "not started" and then flips is worse than one that
  // renders as complete immediately.
  const goalProgress = (
    await getLearningProgress(projectId, version.id).catch(() => null)
  )?.goals.find((item) => item.goal_id === goal.id);

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
        {/* Prerequisites and evidence were on the artifact and rendered nowhere,
            so a reader could not tell what this Goal assumes or what backs it. */}
        {(goal.prerequisite_goal_refs ?? []).length > 0 && (
          <section className="reading-section">
            <p className="eyebrow">BUILDS ON</p>
            <div className="link-list">
              {(goal.prerequisite_goal_refs ?? []).map((id) => {
                const prerequisite = artifactSelectors.getGoal(artifact, id);
                return (
                  <Link
                    href={`/projects/${projectId}/goals/${encodeURIComponent(prerequisite.id)}`}
                    key={prerequisite.id}
                  >
                    {prerequisite.title}
                    <b>↗</b>
                  </Link>
                );
              })}
            </div>
          </section>
        )}

        <EvidencePanel
          projectId={projectId}
          refs={goal.evidence_refs}
          sources={version.evidence_sources ?? {}}
        />

        <ProcessRail artifact={artifact} process={process} projectId={projectId} />
        {/* Interactive here too, not just in Learn Mode. A Practice the learner
            can only read on this page is a dead end. */}
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

