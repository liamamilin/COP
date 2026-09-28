import Link from "next/link";

import { ProjectShell } from "../../../../../components/project-shell";
import { getWorkspace } from "../../../../../lib/api";
import { artifactSelectors } from "../../../../../lib/artifact-selectors";

export default async function ConceptPage({ params }: { params: Promise<{ projectId: string; conceptId: string }> }) {
  const { projectId, conceptId } = await params;
  const { project, version, artifact } = await getWorkspace(projectId);
  const concept = artifactSelectors.getConcept(artifact, decodeURIComponent(conceptId));
  const stages = artifact.stages.filter((stage) => stage.concept_refs.includes(concept.id));
  const operations = (concept.key_operation_refs ?? []).map((id) => artifactSelectors.getOperation(artifact, id));

  return (
    <ProjectShell project={project} version={version} artifact={artifact} active="concept">
      <article className="content-wrap entity-detail-page">
        <header><span className="entity-glyph">C</span><p className="eyebrow">CONCEPT</p><h1>{concept.name}</h1><p className="lead-copy">{concept.definition}</p></header>
        <section><p className="eyebrow">ROLE IN THE SYSTEM</p><h2>{concept.role}</h2></section>
        <section><p className="eyebrow">APPEARS IN</p><div className="link-list">{stages.map((stage) => <Link href={`/projects/${projectId}/stages/${encodeURIComponent(stage.id)}`} key={stage.id}>{stage.title}<b>↗</b></Link>)}</div></section>
        {operations.length > 0 && <section><p className="eyebrow">KEY OPERATIONS</p><div className="link-list">{operations.map((item) => <Link href={`/projects/${projectId}/operations/${encodeURIComponent(item.id)}`} key={item.id}>{item.name}<b>↗</b></Link>)}</div></section>}
      </article>
    </ProjectShell>
  );
}

