import Link from "next/link";

import { ProjectShell } from "../../../../../components/project-shell";
import { getWorkspace } from "../../../../../lib/api";
import { artifactSelectors } from "../../../../../lib/artifact-selectors";

export default async function OperationPage({ params }: { params: Promise<{ projectId: string; operationId: string }> }) {
  const { projectId, operationId } = await params;
  const { project, version, artifact } = await getWorkspace(projectId);
  const operation = artifactSelectors.getOperation(artifact, decodeURIComponent(operationId));
  const stages = artifact.stages.filter((stage) => stage.operation_refs.includes(operation.id));
  const concepts = (operation.acts_on_concept_refs ?? []).map((id) => artifactSelectors.getConcept(artifact, id));

  return (
    <ProjectShell project={project} version={version} artifact={artifact} active="operation">
      <article className="content-wrap entity-detail-page operation-detail">
        <header><span className="entity-glyph">O</span><p className="eyebrow">OPERATION</p><h1>{operation.name}</h1><p className="lead-copy">{operation.definition}</p></header>
        {operation.purpose && <section><p className="eyebrow">PURPOSE</p><h2>{operation.purpose}</h2></section>}
        <section><p className="eyebrow">USED IN STAGES</p><div className="link-list">{stages.map((stage) => <Link href={`/projects/${projectId}/stages/${encodeURIComponent(stage.id)}`} key={stage.id}>{stage.title}<b>↗</b></Link>)}</div></section>
        {concepts.length > 0 && <section><p className="eyebrow">ACTS ON</p><div className="link-list">{concepts.map((item) => <Link href={`/projects/${projectId}/concepts/${encodeURIComponent(item.id)}`} key={item.id}>{item.name}<b>↗</b></Link>)}</div></section>}
      </article>
    </ProjectShell>
  );
}

