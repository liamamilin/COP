import type { COPArtifact, Stage } from "@cop-studio/cop-types";
import Link from "next/link";

import { draftReview } from "../lib/draft-review";

import { ImplementationDetail, StageExample } from "./stage-content";

function DraftStage({ stage, index, projectId }: { stage: Stage; index: number; projectId: string }) {
  return (
    <li>
      <details className="draft-review-stage">
        <summary>
          <span className="draft-review-step-number">{String(index + 1).padStart(2, "0")}</span>
          <span>{stage.title}</span>
          <span className="draft-disclosure-mark" aria-hidden="true">+</span>
        </summary>
        <div className="draft-review-stage-body">
          <p className="draft-stage-outcome">{stage.local_outcome || stage.local_goal}</p>
          {stage.why_it_exists && <p className="muted-note">{stage.why_it_exists}</p>}
          {!!stage.implementation_details?.length && (
            <ol className="detail-list">{stage.implementation_details.map((detail, i) => (
              <ImplementationDetail detail={detail} index={i} key={i} />
            ))}</ol>
          )}
          {stage.example && <StageExample example={stage.example} />}
          <Link className="draft-text-link" href={`/projects/${projectId}/draft/stages/${encodeURIComponent(stage.id)}`}>
            Edit this step ↗
          </Link>
        </div>
      </details>
    </li>
  );
}

/** Presentation only: reading, editing and publishing remain separate actions. */
export function DraftReview({ artifact, projectId }: { artifact: COPArtifact; projectId: string }) {
  const view = draftReview(artifact);
  return (
    <section className="draft-route" id="review-route" aria-labelledby="draft-route-heading">
      <div className="draft-route-heading">
        <div><p className="eyebrow">THE ROUTE</p><h2 id="draft-route-heading">Your learning path</h2></div>
        <p>Open a goal, then a step to read its instructions.</p>
      </div>
      {view.foundations.map(({ foundation, stages }) => (
        <details className="draft-review-foundation" key={foundation.id}>
          <summary><span>Before you start</span><span>{foundation.title}</span><span className="draft-disclosure-mark" aria-hidden="true">+</span></summary>
          <ol className="draft-review-steps">{stages.map((stage, index) => <DraftStage stage={stage} index={index} projectId={projectId} key={stage.id} />)}</ol>
        </details>
      ))}
      <div className="draft-review-goals">
        {view.goals.map(({ goal, processes }, index) => (
          <details className="draft-review-goal" open={index === 0} key={goal.id}>
            <summary>
              <span className="draft-review-goal-number">{String(index + 1).padStart(2, "0")}</span>
              <h3>{goal.title}</h3>
              <span className="draft-review-step-count">{processes.reduce((n, p) => n + p.stages.length, 0)} steps</span>
              <span className="draft-disclosure-mark" aria-hidden="true">+</span>
            </summary>
            <div className="draft-review-goal-body">
              <p className="draft-goal-outcome">{goal.outcome}</p>
              <Link className="draft-text-link" href={`/projects/${projectId}/draft/goals/${encodeURIComponent(goal.id)}`}>Edit goal ↗</Link>
              {processes.map(({ process, stages, practice }) => (
                <div className="draft-review-process" key={process.id}>
                  {processes.length > 1 && <h4>{process.title}</h4>}
                  <ol className="draft-review-steps">{stages.map((stage, i) => <DraftStage stage={stage} index={i} projectId={projectId} key={stage.id} />)}</ol>
                  {practice && (
                    <details className="draft-review-practice">
                      <summary>Check your understanding <span className="draft-disclosure-mark" aria-hidden="true">+</span></summary>
                      <h4>{practice.title}</h4>
                      <ol>{practice.instructions.map((instruction, i) => <li key={i}>{instruction}</li>)}</ol>
                      <p>{practice.expected_outcome}</p>
                      {!!practice.checkpoint_questions?.length && <ul>{practice.checkpoint_questions.map((question, i) => <li key={i}>{question}</li>)}</ul>}
                    </details>
                  )}
                </div>
              ))}
            </div>
          </details>
        ))}
      </div>
    </section>
  );
}
