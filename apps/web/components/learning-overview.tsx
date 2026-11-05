import type { COPArtifact } from "@cop-studio/cop-types";
import Link from "next/link";

import { learningGuide } from "../lib/learning-guide";

/** Presentation only. Original text and canonical order are kept verbatim. */
export function LearningOverview({ artifact, projectId, versionId, title }: {
  artifact: COPArtifact; projectId: string; versionId: string; title: string;
}) {
  const { routes, firstStep, firstGoal } = learningGuide(artifact);
  const learnHref = (goalId?: string, stageId?: string) => {
    const query = new URLSearchParams({ version: versionId });
    if (goalId) query.set("goal", goalId);
    if (stageId) query.set("stage", stageId);
    return `/projects/${projectId}/learn?${query}`;
  };
  const firstAction = firstStep?.implementation_details?.find((detail) => detail.action?.trim())?.action;

  return (
    <>
      <header className="page-header overview-header">
        <div>
          <p className="eyebrow">YOUR PUBLISHED PLAN</p>
          <h1>{title}</h1>
          <p>A learning plan to follow, not work already carried out. Publishing saved this plan; it did not run its steps.</p>
          <div className="workspace-entry-actions">
            <Link className="primary-link" href={learnHref()}>Open Learn →</Link>
            <a className="workspace-text-link" href="#learning-goals">Explore the route ↓</a>
          </div>
        </div>
        <div className="artifact-metrics">
          <span><b>{artifact.goals.length}</b> goals</span>
          <span><b>{artifact.stages.length}</b> steps</span>
        </div>
      </header>

      <section className="learning-brief" aria-label="Understand this plan">
        <p className="eyebrow">THE GENERATED APPROACH</p>
        <h2>What this plan covers</h2>
        <p className="learning-approach">{artifact.domain.name}</p>
        {artifact.domain.non_goals?.[0] && <p className="learning-boundary"><strong>Not included</strong>{artifact.domain.non_goals[0]}</p>}
        <details className="workspace-context">
          <summary>Scope &amp; exclusions — check this matches your intent</summary>
          <p className="eyebrow">SCOPE</p>
          <p>{artifact.domain.scope}</p>
          <p className="eyebrow">WHO THIS IS FOR / STARTING POINT</p>
          <p>{artifact.domain.target_user}</p>
          {!!artifact.domain.non_goals?.length && <>
            <p className="eyebrow">NOT INCLUDED</p>
            <ul className="learning-exclusions">{artifact.domain.non_goals.map((item, i) => <li key={i}>{item}</li>)}</ul>
          </>}
          {!!artifact.shared_foundations.length && <>
            <p className="eyebrow">SHARED PREPARATION</p>
            <ul>{artifact.shared_foundations.map((foundation) => <li key={foundation.id}>
              {foundation.title}
              <ul>{foundation.stage_refs.map((id) => {
                const stage = artifact.stages.find((item) => item.id === id);
                const route = routes.find((item) => item.foundation?.id === foundation.id);
                return stage && <li key={id}><Link className="workspace-text-link" href={route ? learnHref(route.goal.id, id) : `/projects/${projectId}/stages/${encodeURIComponent(id)}`}>{stage.title} →</Link></li>;
              })}</ul>
            </li>)}</ul>
          </>}
          <p className="muted-note">This is the generated scope, not a confirmation of your intent. If it is wrong, revise a draft before following this route.</p>
        </details>
      </section>

      {artifact.mental_model.summary && <section className="learning-brief" aria-label="How the plan fits together">
        <p className="eyebrow">THE PLAN&apos;S EXPLANATION</p>
        <h2>How the ideas fit together</h2>
        <p>{artifact.mental_model.summary}</p>
        <p className="muted-note">This is the saved plan&apos;s explanation, not an independently verified account.</p>
      </section>}

      {firstStep && <section className="learning-start" aria-label="Where to begin">
        <div>
          <p className="eyebrow">FIRST ACTION IN THE PLAN</p>
          <h2>{firstStep.title}</h2>
          <p>{firstAction || firstStep.local_goal}</p>
        </div>
        <Link className="secondary-button" href={learnHref(firstGoal?.id, firstStep.id)}>Open first step →</Link>
      </section>}

      <section className="goal-map" id="learning-goals" aria-labelledby="learning-goals-heading">
        <div className="section-title-row">
          <div><p className="eyebrow">THE ROUTE</p><h2 id="learning-goals-heading">Learning goals</h2></div>
          <p>Read a goal&apos;s outcome, then follow its steps. Terms and sources are available inside each step.</p>
        </div>
        <ol className="learning-route">
          {routes.map(({ goal, stages }, index) => <li className="learning-route-item" key={goal.id}>
            <span className="goal-number">{String(index + 1).padStart(2, "0")}</span>
            <div>
              <p className="learning-route-meta">{stages.length} steps</p>
              <h3><Link href={`/projects/${projectId}/goals/${encodeURIComponent(goal.id)}`}>{goal.title}</Link></h3>
              <details><summary>What you&apos;ll be able to do</summary><p>{goal.outcome}</p></details>
              <Link className="workspace-text-link" href={learnHref(goal.id)}>Follow this goal →</Link>
            </div>
          </li>)}
        </ol>
      </section>

      <details className="learning-background">
        <summary>How this route fits together</summary>
        <section className="mental-model-card">
          <div>
            <p className="eyebrow">MENTAL MODEL</p>
            <h2>How the system moves</h2>
            <ol className="learning-flow">{artifact.mental_model.flow?.map((item, i) => <li key={i}>{item}</li>)}</ol>
          </div>
        </section>
        {!!artifact.expansion_map?.length && <section className="reading-section expansion-map">
          <p className="eyebrow">AFTER THIS PLAN</p><h2>Where to go next</h2>
          <ul>{artifact.expansion_map.map((item, index) => {
            const from = artifact.goals.find((goal) => goal.id === item.from_goal_ref);
            return <li key={index}><div><h3>{item.title}</h3>{item.description && <p>{item.description}</p>}</div>
              {from && <Link href={`/projects/${projectId}/goals/${encodeURIComponent(from.id)}`}>Builds on {from.title} ↗</Link>}
            </li>;
          })}</ul>
        </section>}
      </details>
    </>
  );
}
