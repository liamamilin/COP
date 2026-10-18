"use client";

import { useState } from "react";
import type { COPArtifact } from "@cop-studio/cop-types";

import { artifactSelectors } from "../lib/artifact-selectors";
import { StageContent } from "./stage-content";
import type { ResolvedSource } from "./evidence-panel";

/** Read-only local curriculum review. No project, saved progress or API calls. */
export function BasicPrototypeView({ artifact, sources }: {
  artifact: COPArtifact;
  sources: Record<string, ResolvedSource>;
}) {
  const process = artifact.main_processes[0];
  const foundation = artifact.shared_foundations.find((item) => item.id === process.start.ref);
  const ordered = [...(foundation?.stage_refs ?? []), ...process.stage_refs];
  const [selected, setSelected] = useState(ordered[0]);
  const current = artifactSelectors.getStage(artifact, selected);
  const index = ordered.indexOf(selected);
  const context = artifactSelectors.getStageContext(artifact, current);

  return (
    <section aria-label="Basic prototype learning path">
      <nav className="prototype-stage-tabs" aria-label="Choose a prototype stage">
        {ordered.map((id, number) => {
          const stage = artifactSelectors.getStage(artifact, id);
          return (
            <button type="button" className={id === selected ? "primary-button" : "secondary-button"}
              aria-pressed={id === selected} onClick={() => setSelected(id)} key={id}>
              {number + 1}. {stage.title}
            </button>
          );
        })}
      </nav>
      <article className="stage-content">
        <header className="page-header detail-header">
          <p className="eyebrow">{context.kind === "foundation" ? "FOUNDATION" : "STAGE"} · {index + 1} OF {ordered.length}</p>
          <h2>{current.title}</h2>
          <p className="lead-copy">{current.local_goal}</p>
          <p>{current.why_it_exists}</p>
        </header>
        <StageContent artifact={artifact} projectId="" stage={current} sources={sources} referenceMode="local" />
        {current.local_outcome && <section className="outcome-banner"><span>LOCAL OUTCOME</span><p>{current.local_outcome}</p></section>}
        <nav className="stage-step-navigation" aria-label="Move through the prototype">
          {index > 0 && <button type="button" className="secondary-button" onClick={() => setSelected(ordered[index - 1])}>← Previous</button>}
          {index < ordered.length - 1
            ? <button type="button" className="primary-button" onClick={() => setSelected(ordered[index + 1])}>Next →</button>
            : <a className="primary-button" href="#prototype-practice">Open practice →</a>}
        </nav>
      </article>
    </section>
  );
}
