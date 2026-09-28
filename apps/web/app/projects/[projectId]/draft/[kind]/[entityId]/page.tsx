import Link from "next/link";
import { notFound } from "next/navigation";

import { DraftEditor } from "../../../../../../components/draft-editor";
import { ProjectShell } from "../../../../../../components/project-shell";
import { RefinePanel } from "../../../../../../components/refine-panel";
import { getProjectWorkspace } from "../../../../../../lib/api";
import { editableFields, ENTITY_LABELS } from "../../../../../../lib/draft-editing";
import { DRAFT_EDITABLE_FIELDS, type DraftEntityKind } from "../../../../../../lib/api";

function isDraftEntityKind(value: string): value is DraftEntityKind {
  return value in DRAFT_EDITABLE_FIELDS;
}

export default async function DraftEntityPage({
  params,
}: {
  params: Promise<{ projectId: string; kind: string; entityId: string }>;
}) {
  const { projectId, kind, entityId } = await params;
  if (!isDraftEntityKind(kind)) notFound();
  const decodedId = decodeURIComponent(entityId);

  const { project, version, draft } = await getProjectWorkspace(projectId);
  if (!draft) notFound();

  const fields = editableFields(draft.artifact, kind, decodedId);
  if (fields.length === 0) notFound();

  const label = ENTITY_LABELS[kind];
  const body = (
    <div className="content-wrap narrow-content">
      <header className="page-header detail-header">
        <p className="eyebrow">DRAFT EDITOR · {label.toUpperCase()}</p>
        <h1>{fields.find((field) => field.name === "title" || field.name === "name")?.value ?? decodedId}</h1>
        <p className="lead-copy">
          Changes apply to the draft only. {label} references are structural and are not editable
          here, so the main line cannot be broken from this screen.
        </p>
      </header>

      <p className="draft-entity-id standalone">{decodedId}</p>

      <DraftEditor
        artifact={draft.artifact}
        draftId={draft.id}
        entityId={decodedId}
        kind={kind}
      />

      <RefinePanel
        entityId={decodedId}
        entityKind={kind}
        entityTitle={fields.find((f) => f.name === "title" || f.name === "name")?.value ?? decodedId}
        hasDraft
        projectId={projectId}
      />

      <div className="draft-back-row">
        <Link href={`/projects/${projectId}/draft`}>← Back to draft overview</Link>
      </div>
    </div>
  );

  if (!version) {
    return <div className="workspace standalone-workspace">{body}</div>;
  }
  return (
    <ProjectShell
      active="draft"
      artifact={version.artifact}
      hasDraft
      project={project}
      version={version}
    >
      {body}
    </ProjectShell>
  );
}
