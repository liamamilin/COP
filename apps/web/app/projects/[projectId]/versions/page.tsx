import { ProjectShell } from "../../../../components/project-shell";
import { ExportControls } from "../../../../components/export-controls";
import { StartDraftButton } from "../../../../components/start-draft-button";
import { getProjectWorkspace, getVersions } from "../../../../lib/api";

export const dynamic = "force-dynamic";

export default async function VersionsPage({
  params,
}: {
  params: Promise<{ projectId: string }>;
}) {
  const { projectId } = await params;
  const [{ project, version, draft }, versions] = await Promise.all([
    getProjectWorkspace(projectId),
    getVersions(projectId),
  ]);

  const body = (
    <div className="content-wrap">
      <header className="page-header detail-header">
        <p className="eyebrow">VERSION HISTORY</p>
        <h1>{versions.length} published version{versions.length === 1 ? "" : "s"}</h1>
        <p className="lead-copy">
          Published versions are immutable. Revising one starts a new draft that becomes the next
          version, so the history of what you believed stays readable.
        </p>
      </header>

      {version && (
        <div className="version-actions">
          <p>
            Revising a published version means drafting a copy of it. The version
            itself is never modified.
          </p>
          <StartDraftButton
            existingDraftId={draft?.id ?? null}
            projectId={projectId}
            versionId={version.id}
            versionNumber={version.version_number}
          />
          <ExportControls versionId={version.id} />
        </div>
      )}

      <ol className="version-list">
        {versions.map((item) => {
          const isLatest = item.version_number === version?.version_number;
          return (
            <li className={isLatest ? "version-row latest" : "version-row"} key={item.id}>
              <span className="version-number">v{item.version_number}</span>
              <div>
                <p className="version-summary">{item.change_summary}</p>
                <p className="version-meta">
                  {item.created_by} · {new Date(item.created_at).toLocaleString()}
                  {item.parent_version_id ? " · descends from a previous version" : " · first version"}
                </p>
              </div>
              {isLatest ? (
                <span className="published-state"><i /> Current</span>
              ) : (
                <span className="version-immutable">Immutable</span>
              )}
            </li>
          );
        })}
      </ol>
    </div>
  );

  if (!version) {
    return <div className="workspace standalone-workspace">{body}</div>;
  }
  return (
    <ProjectShell active="versions" artifact={version.artifact} project={project} version={version}>
      {body}
    </ProjectShell>
  );
}
