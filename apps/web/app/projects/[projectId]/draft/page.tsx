import Link from "next/link";
import { notFound } from "next/navigation";

import { DraftToolbar } from "../../../../components/draft-toolbar";
import { DraftReview } from "../../../../components/draft-review";
import { ProjectShell } from "../../../../components/project-shell";
import { getProjectWorkspace } from "../../../../lib/api";
import {
  ENTITY_PLURALS,
  entityCountLabel,
  listEntities,
} from "../../../../lib/draft-editing";
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
    <div className="content-wrap draft-review-page">
      <nav className="draft-breadcrumb" aria-label="Breadcrumb">
        <Link href={`/projects/${projectId}`}>← Project overview</Link><span>/</span><span>Draft review</span>
      </nav>
      <header className="draft-page-header">
        <p className="eyebrow">REVIEW BEFORE YOU PUBLISH</p>
        <h1>{project.title}</h1>
        <p>
          Your learning path is ready. Review the content below, edit anything that needs attention,
          then publish a version to start learning.
        </p>
      </header>

      <ol className="draft-review-guide" aria-label="Next steps">
        <li><span>01</span><div><strong>Review the route</strong><p>Open a goal to read its steps.</p></div></li>
        <li><span>02</span><div><strong>Edit if needed</strong><p>Keep what works; change what doesn&apos;t.</p></div></li>
        <li><span>03</span><div><strong>Publish &amp; learn</strong><p>Save a version in this workspace.</p></div></li>
      </ol>

      <DraftToolbar
        projectId={projectId}
        counts={draft.counts}
        draftId={draft.id}
        hasPublishedVersion={version !== null}
      />

      <DraftReview artifact={draft.artifact} projectId={projectId} />

      <details className="draft-context">
        <summary>About this draft</summary>
        <p>{draft.artifact.domain.scope}</p>
        <p>{draft.artifact.mental_model.summary}</p>
        <Link className="draft-text-link" href={`/projects/${projectId}/sources`}>Review source material ↗</Link>
      </details>

      <details className="draft-advanced">
        <summary>All editable fields <span>Goals, steps, concepts &amp; operations</span></summary>
        <section className="draft-sections">
        {SECTIONS.map((kind) => {
          const entities = listEntities(draft.artifact, kind);
          return (
            <div className="draft-section" key={kind}>
              <div className="section-title-row">
                <div>
                  <p className="eyebrow">{ENTITY_PLURALS[kind].toUpperCase()}</p>
                  <h2>{entityCountLabel(kind, entities.length)}</h2>
                </div>
              </div>
              {entities.length === 0 ? (
                <p className="muted-note">No {ENTITY_PLURALS[kind].toLowerCase()} in this draft.</p>
              ) : (
                <ul className="draft-entity-list">
                  {entities.map((entity) => (
                    <li key={entity.id}>
                      <Link
                        href={`/projects/${projectId}/draft/${kind}/${encodeURIComponent(entity.id)}`}
                      >
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
      </details>
      <div className="draft-review-footer">
        <p>Nothing is published yet. When the route looks right, publish your draft to open Learn mode.</p>
        <a className="draft-text-link" href="#draft-actions">Back to publishing controls ↑</a>
      </div>
    </div>
  );

  if (!version) {
    return <main className="workspace standalone-workspace draft-workspace">{body}</main>;
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
