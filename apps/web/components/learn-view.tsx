"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";

import {
  ApiError,
  putLearningProgress,
  type LearningProgress,
  type StageStatus,
} from "../lib/api";
import { artifactSelectors } from "../lib/artifact-selectors";
import type { COPArtifact, Goal } from "@cop-studio/cop-types";

interface LearnViewProps {
  projectId: string;
  artifact: COPArtifact;
  progress: LearningProgress;
  selectedGoalId: string;
}

/**
 * Learn Mode for one Goal.
 *
 * The whole Main Process is rendered above the fold at all times, which is the
 * product's central claim: you should always be able to see where you are on the
 * main line, not just the step you are standing on. A progress UI that shows
 * only the current Stage would replace that with a tunnel.
 */
export function LearnView({
  projectId,
  artifact,
  progress,
  selectedGoalId,
}: LearnViewProps) {
  const router = useRouter();
  const [pending, setPending] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  // Optimistic overrides, keyed by Stage. Toggling a checkbox should feel
  // instant, and waiting on `router.refresh()` to come back made the control
  // appear to ignore the click.
  const [overrides, setOverrides] = useState<Record<string, StageStatus>>({});

  const goalProgress = progress.goals.find((item) => item.goal_id === selectedGoalId);
  const goal: Goal | undefined = artifact.goals.find((item) => item.id === selectedGoalId);
  const process = goal ? artifactSelectors.getProcessForGoal(artifact, goal.id) : undefined;

  if (!goal || !process || !goalProgress) return null;

  const statusFor = (stageId: string): StageStatus =>
    overrides[stageId] ??
    goalProgress.stages.find((item) => item.stage_id === stageId)?.status ??
    "not_started";

  async function mark(stageId: string, status: StageStatus) {
    setPending(stageId);
    setError(null);
    const previous = statusFor(stageId);
    setOverrides((current) => ({ ...current, [stageId]: status }));
    try {
      await putLearningProgress(projectId, {
        version_id: progress.version_id,
        goal_id: selectedGoalId,
        stage_id: stageId,
        status,
      });
      // Reconcile the rest of the page (goal counters, sidebar) in the
      // background, without making the toggle wait for it.
      router.refresh();
    } catch (cause) {
      setOverrides((current) => ({ ...current, [stageId]: previous }));
      setError(cause instanceof ApiError ? cause.message : "Progress could not be saved.");
    } finally {
      setPending(null);
    }
  }

  const stages = artifactSelectors.getStagesForProcess(artifact, process);
  const practice = artifactSelectors.getPracticeForProcess(artifact, process);
  // The first Stage the user has not finished: where "continue" should land.
  const nextStage = stages.find((stage) => statusFor(stage.id) !== "completed") ?? stages[0];
  const completedCount = stages.filter((stage) => statusFor(stage.id) === "completed").length;
  const goalComplete = stages.length > 0 && completedCount === stages.length;

  return (
    <div className="learn-view">
      <section className="learn-mainline">
        <div className="section-title-row">
          <div>
            <p className="eyebrow">MAIN PROCESS · ALWAYS VISIBLE</p>
            <h2>{process.title}</h2>
            <p className="muted-note">
              {completedCount} of {stages.length} stages complete
              {goalComplete && " · Goal complete"}
            </p>
          </div>
        </div>

        <ol className="learn-stages">
          <li className="learn-stage-zero">
            <span className="learn-stage-index">00</span>
            <div>
              <small>{process.start.type === "foundation" ? "SHARED FOUNDATION" : "ZERO STATE"}</small>
              <strong>
                {artifact.shared_foundations.find((f) => f.id === process.start.ref)?.title ??
                  "Start from zero"}
              </strong>
            </div>
          </li>
          {stages.map((stage, index) => {
            const status = statusFor(stage.id);
            return (
              <li className={`learn-stage ${status}${stage.id === nextStage.id ? " next" : ""}`} key={stage.id}>
                <button
                  aria-label={
                    status === "completed"
                      ? `Reopen stage ${index + 1}`
                      : `Mark stage ${index + 1} complete`
                  }
                  className="learn-stage-toggle"
                  disabled={pending === stage.id}
                  onClick={() =>
                    void mark(stage.id, status === "completed" ? "in_progress" : "completed")
                  }
                  type="button"
                >
                  {status === "completed" ? "✓" : String(index + 1).padStart(2, "0")}
                </button>
                <div className="learn-stage-body">
                  <small>STAGE {index + 1}</small>
                  <strong>{stage.title}</strong>
                  <p>{stage.local_goal}</p>
                </div>
                <a className="secondary-button learn-stage-open" href={`/projects/${projectId}/stages/${encodeURIComponent(stage.id)}`}>
                  Open
                </a>
              </li>
            );
          })}
          <li className="learn-stage-outcome">
            <span className="learn-stage-index">✓</span>
            <div>
              <small>OUTCOME</small>
              <strong>{process.outcome}</strong>
            </div>
          </li>
        </ol>

        {error && (
          <p className="form-error" role="alert">
            {error}
          </p>
        )}
      </section>

      <aside className="learn-detail">
        <div className="learn-detail-card">
          <p className="eyebrow">CURRENT STAGE</p>
          <h3>{nextStage.title}</h3>
          <p className="lead-copy">{nextStage.local_goal}</p>
          {nextStage.why_it_exists && <p className="muted-note">{nextStage.why_it_exists}</p>}

          <h4>Concepts</h4>
          <ul>
            {artifactSelectors.getConceptsForStage(artifact, nextStage).map((concept) => (
              <li key={concept.id}>
                <strong>{concept.name}</strong>
                <span>{concept.definition}</span>
              </li>
            ))}
            {artifactSelectors.getConceptsForStage(artifact, nextStage).length === 0 && (
              <li className="muted-note">No concepts attached to this stage.</li>
            )}
          </ul>

          <h4>Operations</h4>
          <ul>
            {artifactSelectors.getOperationsForStage(artifact, nextStage).map((operation) => (
              <li key={operation.id}>
                <strong>{operation.name}</strong>
                <span>{operation.definition}</span>
              </li>
            ))}
            {artifactSelectors.getOperationsForStage(artifact, nextStage).length === 0 && (
              <li className="muted-note">No operations attached to this stage.</li>
            )}
          </ul>

          {(nextStage.implementation_details ?? []).length > 0 && (
            <>
              <h4>Implementation detail</h4>
              <ul>
                {(nextStage.implementation_details ?? []).map((detail, index) => (
                  <li key={index}>
                    <strong>{String(detail.title ?? detail.name ?? `Detail ${index + 1}`)}</strong>
                    <span>{String(detail.description ?? "")}</span>
                  </li>
                ))}
              </ul>
            </>
          )}

          {nextStage.example && (
            <div className="learn-example">
              <h4>Example</h4>
              <p>{String(nextStage.example.summary ?? "")}</p>
            </div>
          )}

          {practice && (
            <div className="learn-practice">
              <h4>Minimal Practice</h4>
              <p className="muted-note">{practice.title}</p>
              <ol>
                {practice.instructions.map((instruction) => (
                  <li key={instruction}>{instruction}</li>
                ))}
              </ol>
              {(practice.checkpoint_questions ?? []).length > 0 && (
                <>
                  <h4>Checkpoints</h4>
                  <ul>
                    {(practice.checkpoint_questions ?? []).map((question) => (
                      <li key={question}>{question}</li>
                    ))}
                  </ul>
                </>
              )}
            </div>
          )}
        </div>
      </aside>
    </div>
  );
}
