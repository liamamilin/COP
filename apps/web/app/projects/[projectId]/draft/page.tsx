import Link from "next/link";
import { notFound } from "next/navigation";

import { DraftToolbar } from "../../../../components/draft-toolbar";
import { ProjectShell } from "../../../../components/project-shell";
import { getProjectWorkspace } from "../../../../lib/api";
import { ENTITY_LABELS, listEntities } from "../../../../lib/draft-editing";
import type { DraftEntityKind } from "../../../../lib/api";

const SECTIONS: DraftEntityKind[] = ["goals", "processes", "stages", "concepts", "operations"];

export default async function DraftPage({
  params,
}: {
  params: Promise<{ projectId: string }>;
}) {
  const { projectId } = await params;
  const { project, version, draft } = await getProjectWorkspace(projectId);
  if (!draft) notFound();

  // The shell renders the published workspace chrome. A draft on a project with
  // no published version yet has nothing to show there, so this page supplies a
  // minimal frame of its own rather than pretending a version exists.
  const body = (
    <div className="content-wrap">
      <header className="page-header detail-header">
        <p className="eyebrow">DRAFT · EDITABLE</p>
        <h1>{draft.title || project.title}</h1>
        <p className="lead-copy">
          This is your working copy. Edits here never touch a published version; publishing is a
          separate, explicit step.
        </p>
      </header>

      <DraftToolbar
        counts={draft.counts}
        draftId={draft.id}
        hasPublishedVersion={version !== null}
      />

      <section className="draft-sections">
        {SECTIONS.map((kind) => {
          const entities = listEntities(draft.artifact, kind);
          return (
            <div className="draft-section" key={kind}>
              <div className="section-title-row">
                <div>
                  <p className="eyebrow">{ENTITY_LABELS[kind].toUpperCase()}S</p>
                  <h2>
                    {entities.length} {ENTITY_LABELS[kind].toLowerCase()}
                    {entities.length === 1 ? "" : "s"}
                  </h2>
                </div>
              </div>
              {entities.length === 0 ? (
                <p className="muted-note">No {ENTITY_LABELS[kind].toLowerCase()}s in this draft.</p>
              ) : (
                <ul className="draft-entity-list">
                  {entities.map((entity) => (
                    <li key={entity.id}>
                      <Link
                        href={`/projects/${projectId}/draft/${kind}/${encodeURIComponent(entity.id)}`}
                      >
                        <span className="draft-entity-id">{entity.id}</span>
                        <strong>{entity.title}</strong>
                        <span className="goal-enter">Edit <b>↗</b></span>
                      </Link>
                    </li>
                  ))}
                </ul>
              )}
            </div>
          );
        })}
      </section>
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
