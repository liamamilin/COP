import type { COPArtifact, Stage } from "@cop-studio/cop-types";

import { artifactSelectors } from "../lib/artifact-selectors";

interface Props {
  artifact: COPArtifact;
  projectId: string;
  stage: Stage;
}

export function StageContextNavigation({ artifact, projectId, stage }: Props) {
  const context = artifactSelectors.getStageContext(artifact, stage);
  const stageHref = (id: string) => `/projects/${projectId}/stages/${encodeURIComponent(id)}`;
  return (
    <aside className="stage-context">
      {context.prerequisites.length > 0 && (
        <nav aria-label="Foundation prerequisites">
          <p className="eyebrow">SHARED FOUNDATION · BEFORE THIS PROCESS</p>
          {context.prerequisites.map((item, index) => (
            <a href={stageHref(item.id)} key={item.id}><span>{index + 1}</span>{item.title}</a>
          ))}
        </nav>
      )}
      <nav aria-label={context.kind === "foundation" ? "Foundation stages" : "Process stages"}>
        <p className="eyebrow">{context.kind === "foundation" ? "FOUNDATION CONTEXT" : "PROCESS CONTEXT"}</p>
        <h3>{context.title}</h3>
        {context.stages.map((item, index) => (
          <a className={item.id === stage.id ? "current" : ""} aria-current={item.id === stage.id ? "step" : undefined}
            href={stageHref(item.id)} key={item.id}>
            <span>{String(index + 1).padStart(2, "0")}</span>{item.title}
          </a>
        ))}
      </nav>
    </aside>
  );
}

export function StageStepNavigation({ artifact, projectId, stage }: Props) {
  const context = artifactSelectors.getStageContext(artifact, stage);
  const previous = context.stages[context.index - 1] ?? context.prerequisites.at(-1);
  const next = context.stages[context.index + 1];
  const stageHref = (id: string) => `/projects/${projectId}/stages/${encodeURIComponent(id)}`;
  return (
    <nav className="stage-step-navigation" aria-label="Continue the learning path">
      {previous && <a className="secondary-button" href={stageHref(previous.id)}>← Previous: {previous.title}</a>}
      {next && <a className="primary-button" href={stageHref(next.id)}>Next: {next.title} →</a>}
      {!next && context.process && (
        <a className="primary-button" href={`/projects/${projectId}/processes/${encodeURIComponent(context.process.id)}`}>
          Open process and practice →
        </a>
      )}
      {!next && context.continuations.length === 1 && context.continuations[0].stage_refs[0] && (
        <a className="primary-button" href={stageHref(context.continuations[0].stage_refs[0])}>
          Continue: {context.continuations[0].title} →
        </a>
      )}
      {!next && context.continuations.length > 1 && (
        <div>
          <p className="eyebrow">CHOOSE A PROCESS AFTER THIS FOUNDATION</p>
          {context.continuations.map((process) => (
            <a className="secondary-button" href={`/projects/${projectId}/processes/${encodeURIComponent(process.id)}`} key={process.id}>
              Continue: {process.title} →
            </a>
          ))}
        </div>
      )}
    </nav>
  );
}
