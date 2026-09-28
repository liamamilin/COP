import { ProjectSettingsForm } from "../../../../components/project-settings-form";
import { ProjectSetupShell } from "../../../../components/project-setup-shell";
import { ProjectShell } from "../../../../components/project-shell";
import { ApiError, getLatestVersion, getProject } from "../../../../lib/api";

export default async function ProjectSettingsPage({ params }: { params: Promise<{ projectId: string }> }) {
  const { projectId } = await params;
  const project = await getProject(projectId);
  let version = null;
  try { version = await getLatestVersion(projectId); } catch (error) {
    if (!(error instanceof ApiError) || error.status !== 404) throw error;
  }
  const content = <div className="content-wrap settings-page"><header className="page-header detail-header"><p className="eyebrow">PROJECT SETTINGS</p><h1>Keep the scope<br />intentional.</h1><p className="lead-copy">Metadata changes do not rewrite published COP versions.</p></header><ProjectSettingsForm project={project} /></div>;
  return version ? <ProjectShell project={project} version={version} artifact={version.artifact} active="settings">{content}</ProjectShell> : <ProjectSetupShell project={project} active="settings">{content}</ProjectSetupShell>;
}
