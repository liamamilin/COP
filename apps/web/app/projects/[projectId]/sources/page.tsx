import { ProjectSetupShell } from "../../../../components/project-setup-shell";
import { ProjectShell } from "../../../../components/project-shell";
import { SourceManager } from "../../../../components/source-manager";
import { ApiError, getLatestVersion, getProject, getProjectSources } from "../../../../lib/api";

export default async function SourcesPage({ params }: { params: Promise<{ projectId: string }> }) {
  const { projectId } = await params;
  const [project, sources] = await Promise.all([getProject(projectId), getProjectSources(projectId)]);
  let version = null;
  try { version = await getLatestVersion(projectId); } catch (error) {
    if (!(error instanceof ApiError) || error.status !== 404) throw error;
  }
  const content = <div className="content-wrap source-page"><header className="page-header detail-header"><p className="eyebrow">SOURCE MANAGER</p><h1>Evidence in,<br />structure out.</h1><p className="lead-copy">Sources support the COP, but they do not dictate its chapter order.</p></header><SourceManager projectId={projectId} initialSources={sources} /></div>;
  return version ? <ProjectShell project={project} version={version} artifact={version.artifact} active="sources">{content}</ProjectShell> : <ProjectSetupShell project={project} active="sources">{content}</ProjectSetupShell>;
}

