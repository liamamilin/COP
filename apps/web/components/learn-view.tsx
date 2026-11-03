"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";

import {
  ApiError,
  putLearningProgress,
  type LearningProgress,
  type ProgressUpdate,
  type StageStatus,
} from "../lib/api";
import { artifactSelectors } from "../lib/artifact-selectors";
import { selectLearningStep } from "../lib/learning-guide";
import { PracticeCard } from "./practice-card";
import { StageContent } from "./stage-content";
import type { ResolvedSource } from "./evidence-panel";
import type { COPArtifact, Goal } from "@cop-studio/cop-types";

interface LearnViewProps {
  projectId: string;
  artifact: COPArtifact;
  progress: LearningProgress;
  selectedGoalId: string;
  selectedStageId?: string;
  /** Backend-resolved evidence, so a citation is either openable or labelled. */
  sources: Record<string, ResolvedSource>;
}

/**
 * Learn Mode for one Goal.
 *
 * The whole route remains available alongside the active step (below it on
 * small screens), rather than being replaced by the active step. Viewing and
 * navigating never write progress; only the explicit completion controls do.
 */
export function LearnView({
  projectId,
  artifact,
  progress,
  selectedGoalId,
  selectedStageId,
  sources,
}: LearnViewProps) {
  const router = useRouter();
  const [pending, setPending] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  // Optimistic overrides. Keyed by activity, so a Stage, a Foundation Stage and
  // a Practice can all be toggled without waiting for a round trip; waiting on
  // `router.refresh()` made the control look like it ignored the click.
  const [overrides, setOverrides] = useState<Record<string, StageStatus>>({});
  // Checkpoint answers are not a status, so they get their own optimistic map.
  const [answerOverrides, setAnswerOverrides] = useState<Record<string, string>>({});

  const goalProgress = progress.goals.find((item) => item.goal_id === selectedGoalId);
  const goal: Goal | undefined = artifact.goals.find((item) => item.id === selectedGoalId);
  const process = goal ? artifactSelectors.getProcessForGoal(artifact, goal.id) : undefined;

  if (!goal || !process || !goalProgress) return null;

  const statusFor = (stageId: string): StageStatus =>
    overrides[`stage:${stageId}`] ??
    goalProgress.stages.find((item) => item.stage_id === stageId)?.status ??
    "not_started";

  // The Foundation is stored once per version and belongs to no Goal, which is
  // what stops the same shared setup being tracked once per Goal.
  const foundationStatusFor = (stageId: string): StageStatus =>
    overrides[`foundation:${stageId}`] ??
    progress.foundations.find((item) => item.stage_id === stageId)?.status ??
    "not_started";

  const checkpoints = (goalProgress.practice?.checkpoints ?? []).map((item) => ({
    ...item,
    answer: answerOverrides[item.question] ?? item.answer,
  }));

  // Derived the same way the server derives it, plus the answers the user has
  // just typed. Two ordering rules, both load-bearing:
  //   a local override wins, so a click is reflected immediately;
  //   the server's `completed` wins over the "has an answer" inference, so a
  //     completed Practice does not revert to "in progress" the moment a
  //     `router.refresh()` brings the saved answers back.
  const answeredCount = checkpoints.filter((item) => (item.answer ?? "").trim().length > 0)
    .length;
  const serverPracticeStatus = goalProgress.practice?.status ?? "not_started";
  const inferred: StageStatus = answeredCount > 0 ? "in_progress" : serverPracticeStatus;
  const practiceStatus: StageStatus =
    overrides[`practice:${goal.id}`] ??
    (serverPracticeStatus === "completed" ? "completed" : inferred);

  async function record(body: Omit<ProgressUpdate, "version_id">) {
    setPending(body.stage_id ?? body.kind);
    setError(null);
    const key = `${body.kind}:${body.stage_id ?? body.goal_id}`;
    const previous = overrides[key];
    setOverrides((current) => ({ ...current, [key]: body.status }));
    try {
      await putLearningProgress(projectId, { ...body, version_id: progress.version_id });
      // Reconcile counters and the sidebar in the background, without making
      // the control wait for it.
      router.refresh();
    } catch (cause) {
      if (previous) {
        setOverrides((current) => ({ ...current, [key]: previous }));
      } else {
        setOverrides((current) => {
          const next = { ...current };
          delete next[key];
          return next;
        });
      }
      setError(cause instanceof ApiError ? cause.message : "Progress could not be saved.");
    } finally {
      setPending(null);
    }
  }

  async function mark(stageId: string, status: StageStatus) {
    await record({
      kind: "stage",
      goal_id: selectedGoalId,
      stage_id: stageId,
      status,
    });
  }

  async function markFoundation(stageId: string, status: StageStatus) {
    await record({ kind: "foundation", goal_id: "", stage_id: stageId, status });
  }

  async function answerCheckpoint(question: string, answer: string) {
    const previous = answerOverrides[question];
    setAnswerOverrides((current) => ({ ...current, [question]: answer }));
    setError(null);
    try {
      await putLearningProgress(projectId, {
        kind: "checkpoint",
        goal_id: selectedGoalId,
        stage_id: question,
        status: "completed",
        notes: answer,
        version_id: progress.version_id,
      });
      router.refresh();
    } catch (cause) {
      if (previous === undefined) {
        setAnswerOverrides((current) => {
          const next = { ...current };
          delete next[question];
          return next;
        });
      } else {
        setAnswerOverrides((current) => ({ ...current, [question]: previous }));
      }
      setError(cause instanceof ApiError ? cause.message : "The answer could not be saved.");
    }
  }

  const stages = artifactSelectors.getStagesForProcess(artifact, process);
  const practice = artifactSelectors.getPracticeForProcess(artifact, process);
  // The first Stage the user has not finished: where "continue" should land.
  const nextStage = stages.find((stage) => statusFor(stage.id) !== "completed") ?? stages[0];
  const preparation = artifact.shared_foundations.find((item) => item.id === process.start.ref);
  const preparationStages = (preparation?.stage_refs ?? []).map((id) => artifactSelectors.getStage(artifact, id));
  const { stage: currentStage, ordered, isFoundation } = selectLearningStep({
    stages, foundations: preparationStages, selectedStageId, statusFor, foundationStatusFor,
  });
  const currentIndex = ordered.findIndex((stage) => stage.id === currentStage.id);
  const currentStatus = isFoundation ? foundationStatusFor(currentStage.id) : statusFor(currentStage.id);
  const stageHref = (stageId: string) =>
    `/projects/${projectId}/learn?goal=${encodeURIComponent(selectedGoalId)}` +
    `&version=${encodeURIComponent(progress.version_id)}` +
     `&stage=${encodeURIComponent(stageId)}#current-step`;
  const completedCount = stages.filter((stage) => statusFor(stage.id) === "completed").length;
  // Derived the same way the server derives it, so the "Goal complete" line can
  // never disagree with the badge on the Goal list. The server's `blocked_by` is
  // the authority; these are the optimistic view of it.
  const foundationStages = progress.foundations;
  const foundationsDone = foundationStages.filter(
    (item) => foundationStatusFor(item.stage_id) === "completed",
  ).length;
  const allCheckpointsAnswered =
    checkpoints.length > 0 &&
    checkpoints.every((item) => (item.answer ?? "").trim().length > 0);
  const goalComplete =
    stages.length > 0 &&
    completedCount === stages.length &&
    foundationsDone === foundationStages.length &&
    (goalProgress.practice === null || practiceStatus === "completed") &&
    (goalProgress.practice === null || allCheckpointsAnswered);

  return (
    <div className="learn-view">
      <section className="learn-goal-context" aria-label="Current goal">
        <p className="eyebrow">YOU ARE WORKING TOWARDS</p>
        {goal.why_it_matters && <div className="learn-goal-rationale">
          <h2>Why this goal is in the plan</h2>
          <p>{goal.why_it_matters}</p>
        </div>}
        <details>
          <summary>{goal.title}</summary>
          <p>{goal.outcome}</p>
          {!!goal.prerequisite_goal_refs?.length && <>
            <p className="eyebrow">EARLIER GOALS IN THIS PLAN</p>
            <ul>{goal.prerequisite_goal_refs.map((id) => {
              const prerequisite = artifact.goals.find((item) => item.id === id);
              return prerequisite && <li key={id}><a className="workspace-text-link" href={`/projects/${projectId}/learn?goal=${encodeURIComponent(id)}&version=${encodeURIComponent(progress.version_id)}`}>{prerequisite.title} →</a></li>;
            })}</ul>
          </>}
        </details>
      </section>
      {/* The shared setup, once. Every Main Process starts here, so it is a
          single checklist rather than something repeated per Goal. */}
      {foundationStages.length > 0 && (
        <section className="learn-foundation">
          <div className="section-title-row">
            <div>
              <p className="eyebrow">SHARED FOUNDATION · ONCE FOR EVERY GOAL</p>
              <h2>
                {foundationsDone} of {foundationStages.length} complete
              </h2>
            </div>
          </div>
          <ul>
            {foundationStages.map((item) => {
              const stage = artifact.stages.find((s) => s.id === item.stage_id);
              const status = foundationStatusFor(item.stage_id);
              return (
                <li key={item.stage_id}>
                  <div className="learn-foundation-content">
                    {stage ? (
                      <details>
                        <summary>Open foundation: {stage.title}</summary>
                         <StageContent artifact={artifact} projectId={projectId} stage={stage} sources={sources} />
                         <a className="workspace-text-link" href={stageHref(stage.id)}>Read this preparation step →</a>
                      </details>
                    ) : <span>{item.stage_id}</span>}
                  </div>
                  <button
                    className={status === "completed" ? "secondary-button" : "primary-button"}
                    disabled={pending === item.stage_id}
                    onClick={() =>
                      void markFoundation(
                        item.stage_id,
                        status === "completed" ? "in_progress" : "completed",
                      )
                    }
                    type="button"
                  >
                    {status === "completed" ? "Reopen" : "Mark complete"}
                  </button>
                </li>
              );
            })}
          </ul>
        </section>
      )}

      <section className="learn-mainline" id="learn-route" aria-label="Steps in this goal">
        <div className="section-title-row">
          <div>
            <p className="eyebrow">YOUR ROUTE</p>
            <h2>Steps in this goal</h2>
            <p className="muted-note">
              {completedCount} of {stages.length} steps marked complete
                {goalComplete && " · Goal complete"}
            </p>
          </div>
        </div>

        <ol className="learn-stages">
          <li className="learn-stage-zero">
            <span className="learn-stage-index">00</span>
            <div>
              <small>{process.start.type === "foundation" ? "SHARED PREPARATION" : "STARTING POINT"}</small>
              <strong>
                {artifact.shared_foundations.find((f) => f.id === process.start.ref)?.title ??
                  "No shared preparation listed"}
              </strong>
            </div>
          </li>
          {stages.map((stage, index) => {
            const status = statusFor(stage.id);
            return (
              <li className={`learn-stage ${status}${stage.id === nextStage.id ? " next" : ""}${stage.id === currentStage.id ? " is-current" : ""}`} key={stage.id}>
                <button
                  aria-label={
                    status === "completed"
                      ? `Reopen stage ${index + 1}`
                      : `Mark stage ${index + 1} complete`
                  }
                   className="learn-stage-toggle"
                   title={status === "completed" ? `Reopen step ${index + 1}` : `Mark step ${index + 1} complete`}
                  disabled={pending === stage.id}
                  onClick={() =>
                    void mark(stage.id, status === "completed" ? "in_progress" : "completed")
                  }
                  type="button"
                >
                   {status === "completed" ? "✓" : "○"}
                </button>
                <div className="learn-stage-body">
                   <small>STEP {index + 1}{stage.id === currentStage.id ? " · READING NOW" : ""}</small>
                  <strong>{stage.title}</strong>
                </div>
                <a className="secondary-button learn-stage-open" aria-current={stage.id === currentStage.id ? "step" : undefined} href={stageHref(stage.id)}>
                  Read step
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

      <article className="learn-detail" id="current-step" aria-label="Current step instructions">
        <div className="learn-detail-card">
          <p className="eyebrow">{isFoundation ? "PREPARATION" : "CURRENT STEP"} · {currentIndex + 1} OF {ordered.length}</p>
          {/* Own class rather than a bare `h3` selector. The card now also holds
              the Practice, which has its own heading, so "the title of the Stage
              being shown" needs to be addressable on its own instead of by
              position among whatever else the card contains. */}
          <h3 className="learn-current-stage-title">{currentStage.title}</h3>
          <a className="workspace-text-link learn-route-jump" href="#learn-route">See all steps in this goal ↓</a>

          <div className="learn-stage-content">
            <StageContent artifact={artifact} projectId={projectId} sources={sources} stage={currentStage} />
          </div>

          <p className="step-reading-note">Mark complete only after checking your result. Previous and Next change the step you read; they do not save completion.</p>

          <div className="learn-stage-navigation" aria-label="Move through stages">
            {currentIndex > 0 ? (
              <a className="secondary-button" href={stageHref(ordered[currentIndex - 1].id)}>Previous</a>
            ) : <span />}
            <button
              className="primary-button"
              disabled={pending === currentStage.id}
              onClick={() =>
                void (isFoundation ? markFoundation : mark)(currentStage.id,
                  currentStatus === "completed" ? "in_progress" : "completed")
              }
              type="button"
            >
              {currentStatus === "completed" ? "Reopen stage" : "Mark complete"}
            </button>
            {currentIndex < ordered.length - 1 ? (
              <a className="secondary-button" href={stageHref(ordered[currentIndex + 1].id)}>Next</a>
            ) : <span />}
          </div>

          {!isFoundation && practice && <details className="learn-practice-disclosure" open={currentIndex === ordered.length - 1}>
            <summary>After the steps: check your understanding</summary>
            <PracticeCard
              disabled={pending === `practice:${goal.id}`}
              onAnswerCheckpoint={(question, answer) => void answerCheckpoint(question, answer)}
              onRecordPractice={(status) =>
                void record({ kind: "practice", goal_id: goal.id, status })
              }
              practice={practice}
              progress={{
                practice_id: practice.id,
                title: practice.title,
                status: practiceStatus,
                checkpoints,
                updated_at: goalProgress.practice?.updated_at ?? null,
              }}
            />
          </details>}
        </div>
      </article>
    </div>
  );
}
