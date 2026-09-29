import { notFound } from "next/navigation";

import { LearnView } from "../../../../components/learn-view";
import { ProjectShell } from "../../../../components/project-shell";
import {
  getLatestVersion,
  getLearningProgress,
  getProject,
  getVersion,
  getVersions,
} from "../../../../lib/api";

/**
 * Learn Mode.
 *
 * Progress is fetched for the *latest* version by default, and the version id
 * is carried in the URL when one is chosen explicitly, so a stale tab writes
 * back into the history it was opened on rather than the newest one.
 */
export default async function LearnPage({
  params,
  searchParams,
}: {
  params: Promise<{ projectId: string }>;
  searchParams: Promise<{ goal?: string; version?: string; stage?: string }>;
}) {
  const { projectId } = await params;
  const { goal: goalParam, version: versionParam, stage: stageParam } = await searchParams;

  const [project, version, versions] = await Promise.all([
    getProject(projectId),
    versionParam ? getVersion(versionParam) : getLatestVersion(projectId),
    getVersions(projectId),
  ]).catch(() => [null, null, []] as const);
  if (!project || !version || version.project_id !== projectId) notFound();

  const progress = await getLearningProgress(projectId, version.id).catch(() => null);
  if (!progress) notFound();

  const selectedGoalId = goalParam ?? progress.goals[0]?.goal_id;
  if (!selectedGoalId) notFound();

  return (
    <ProjectShell active="learn" artifact={version.artifact} project={project} version={version}>
      <div className="content-wrap">
        <header className="page-header detail-header">
          <p className="eyebrow">LEARN · VERSION {progress.version_number}</p>
          <h1>Work the main line.</h1>
          <p className="lead-copy">
            The whole process stays on screen while you move through it. Your place is saved as
            you go.
          </p>
        </header>

        <nav className="learn-versions" aria-label="Choose an artifact version">
          {versions.map((item) => (
            <a
              className={item.id === version.id ? "active" : ""}
              href={`/projects/${projectId}/learn?version=${item.id}`}
              key={item.id}
            >
              v{item.version_number}
            </a>
          ))}
        </nav>

        <nav className="learn-goals" aria-label="Choose a goal">
          {progress.goals.map((item) => {
            const active = item.goal_id === selectedGoalId;
            const href = `/projects/${projectId}/learn?goal=${encodeURIComponent(item.goal_id)}&version=${progress.version_id}`;
            return (
              <a
                className={active ? "learn-goal active" : "learn-goal"}
                href={href}
                key={item.goal_id}
              >
                <span className="learn-goal-progress">
                  {item.completed ? "✓" : `${item.completed_stages}/${item.total_stages}`}
                </span>
                <strong>{item.title}</strong>
              </a>
            );
          })}
        </nav>

        <LearnView
          artifact={version.artifact}
          projectId={projectId}
          progress={progress}
          selectedGoalId={selectedGoalId}
          selectedStageId={stageParam}
        />
      </div>
    </ProjectShell>
  );
}
