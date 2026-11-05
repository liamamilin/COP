import { ProjectSetupShell } from "../../../../components/project-setup-shell";
import { ProjectShell } from "../../../../components/project-shell";
import { SourceManager } from "../../../../components/source-manager";
import { getProjectSources, getProjectWorkspace } from "../../../../lib/api";

export default async function SourcesPage({ params }: { params: Promise<{ projectId: string }> }) {
  const { projectId } = await params;
  const [{ project, version, draft }, sources] = await Promise.all([
    getProjectWorkspace(projectId), getProjectSources(projectId),
  ]);
  const content = <div className="content-wrap source-page"><header className="page-header detail-header"><p className="eyebrow">SOURCE MANAGER</p><h1>Evidence in,<br />structure out.</h1><p className="lead-copy">Sources support the COP, but they do not dictate its chapter order.</p></header><SourceManager projectId={projectId} initialSources={sources} /></div>;
  return version ? <ProjectShell project={project} version={version} artifact={version.artifact} active="sources" hasDraft={draft !== null}>{content}</ProjectShell> : <ProjectSetupShell project={project} active="sources" hasDraft={draft !== null}>{content}</ProjectSetupShell>;
}
