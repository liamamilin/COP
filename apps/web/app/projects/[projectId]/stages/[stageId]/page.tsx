import Link from "next/link";

import { ProjectShell } from "../../../../../components/project-shell";
import { getWorkspace } from "../../../../../lib/api";
import { artifactSelectors } from "../../../../../lib/artifact-selectors";

export default async function StagePage({
  params,
}: {
  params: Promise<{ projectId: string; stageId: string }>;
}) {
  const { projectId, stageId } = await params;
  const { project, version, artifact } = await getWorkspace(projectId);
  const stage = artifactSelectors.getStage(artifact, decodeURIComponent(stageId));
  const concepts = artifactSelectors.getConceptsForStage(artifact, stage);
  const operations = artifactSelectors.getOperationsForStage(artifact, stage);
  const branches = artifactSelectors.getBranchesForStage(artifact, stage);
  const process = artifact.main_processes.find((item) => item.stage_refs.includes(stage.id));
  const stageIndex = process?.stage_refs.indexOf(stage.id) ?? -1;

  return (
    <ProjectShell project={project} version={version} artifact={artifact} active="stage">
      <div className="content-wrap stage-layout">
        <aside className="stage-context">
          <p className="eyebrow">PROCESS CONTEXT</p>
          <h3>{process?.title ?? "Shared foundation"}</h3>
          {process?.stage_refs.map((id, index) => {
            const item = artifactSelectors.getStage(artifact, id);
            return (
              <Link className={item.id === stage.id ? "current" : ""} href={`/projects/${projectId}/stages/${encodeURIComponent(id)}`} key={id}>
                <span>{String(index + 1).padStart(2, "0")}</span>{item.title}
              </Link>
            );
          })}
        </aside>

        <article className="stage-content">
          <header className="page-header detail-header">
            <p className="eyebrow">STAGE {stageIndex >= 0 ? stageIndex + 1 : "FOUNDATION"}</p>
            <h1>{stage.title}</h1>
            <div className="local-goal-block">
              <span>LOCAL GOAL</span>
              <p>{stage.local_goal}</p>
            </div>
          </header>

          {stage.why_it_exists && (
            <section className="reading-section">
              <p className="eyebrow">WHY THIS EXISTS</p>
              <p className="lead-copy">{stage.why_it_exists}</p>
            </section>
          )}

          <section className="reading-section">
            <p className="eyebrow">CONCEPTS × OPERATIONS</p>
            <div className="entity-columns">
              <div>
                <h2>Concepts</h2>
                {concepts.map((concept) => (
                  <Link className="entity-card" href={`/projects/${projectId}/concepts/${encodeURIComponent(concept.id)}`} key={concept.id}>
                    <span>C</span><div><h3>{concept.name}</h3><p>{concept.definition}</p></div><b>↗</b>
                  </Link>
                ))}
              </div>
              <div>
                <h2>Operations</h2>
                {operations.map((operation) => (
                  <Link className="entity-card operation-card" href={`/projects/${projectId}/operations/${encodeURIComponent(operation.id)}`} key={operation.id}>
                    <span>O</span><div><h3>{operation.name}</h3><p>{operation.definition}</p></div><b>↗</b>
                  </Link>
                ))}
              </div>
            </div>
          </section>

          {stage.local_outcome && (
            <section className="outcome-banner"><span>LOCAL OUTCOME</span><p>{stage.local_outcome}</p></section>
          )}

          {branches.length > 0 && (
            <section className="reading-section">
              <p className="eyebrow">BRANCHES</p>
              {branches.map((branch) => (
                <div className="branch-row" key={branch.id}><span>{branch.type}</span><div><h3>{branch.title}</h3><p>{branch.description}</p></div></div>
              ))}
            </section>
          )}
        </article>
      </div>
    </ProjectShell>
  );
}

