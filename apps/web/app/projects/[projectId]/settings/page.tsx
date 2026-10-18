import { ProjectSettingsForm } from "../../../../components/project-settings-form";
import { ProjectSetupShell } from "../../../../components/project-setup-shell";
import { ProjectShell } from "../../../../components/project-shell";
import {
  ApiError,
  getLatestVersion,
  getProject,
  getProjectSettings,
  type ProjectSettingsView,
} from "../../../../lib/api";

export default async function ProjectSettingsPage({
  params,
}: {
  params: Promise<{ projectId: string }>;
}) {
  const { projectId } = await params;
  const project = await getProject(projectId);

  let version = null;
  try {
    version = await getLatestVersion(projectId);
  } catch (error) {
    if (!(error instanceof ApiError) || error.status !== 404) throw error;
  }

  // Fetched here rather than in the client component so the first paint already
  // shows the effective values. A settings form that renders blanks and then
  // fills in is indistinguishable from one that failed to load.
  let settings: ProjectSettingsView;
  try {
    settings = await getProjectSettings(projectId);
  } catch (error) {
    // A missing settings row is not an error: every project has effective
    // settings, they simply may not have overrides yet.
    if (!(error instanceof ApiError)) throw error;
    settings = {
      overrides: {},
      effective: {
        generation: {
          language: project.preferred_language,
          generation_depth: "standard",
          learner_level: "new",
          detail_density: "balanced",
          practice_mode: "priority",
          evidence_density: "key_claims",
        },
      } as ProjectSettingsView["effective"],
    };
  }

  const content = (
    <div className="content-wrap settings-page">
      <header className="page-header detail-header">
        <p className="eyebrow">PROJECT SETTINGS</p>
        <h1>
          Keep the scope
          <br />
          intentional.
        </h1>
        <p className="lead-copy">
          Metadata changes do not rewrite published COP versions. Generation overrides apply to the
          next run, and never retroactively to a published version.
        </p>
      </header>
      <ProjectSettingsForm project={project} effective={settings} />
    </div>
  );

  return version ? (
    <ProjectShell project={project} version={version} artifact={version.artifact} active="settings">
      {content}
    </ProjectShell>
  ) : (
    <ProjectSetupShell project={project} active="settings">
      {content}
    </ProjectSetupShell>
  );
}
