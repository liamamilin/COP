import { ProjectLibrary } from "../components/project-library";
import { getArchivedProjects, getLatestVersion, getProjects, type ProjectSummary } from "../lib/api";
import { projectPreview, type ProjectPreview } from "../lib/project-preview";

/**
 * The library.
 *
 * Active and archived are counted separately and shown separately. Hiding an
 * archived project without saying where it went is how a user concludes the app
 * lost their work, and spec `18` requires a project list that survives a restart
 * -- which it does, but only visibly.
 */
export default async function HomePage() {
  let active: ProjectSummary[] = [];
  let archived: ProjectSummary[] = [];
  let unavailable = false;
  try {
    [active, archived] = await Promise.all([getProjects(), getArchivedProjects()]);
  } catch {
    unavailable = true;
  }

  // Optional read-only previews. Cap these reads for large libraries; a failed
  // preview never hides a project or prevents entry into its workspace.
  const previews: Record<string, ProjectPreview> = {};
  if (!unavailable) {
    await Promise.all(active.filter((project) => project.latest_version !== null).slice(0, 6).map(async (project) => {
      try {
        previews[project.id] = projectPreview((await getLatestVersion(project.id)).artifact);
      } catch {
        // The basic project card remains usable without a published preview.
      }
    }));
  }
  return <ProjectLibrary active={active} archived={archived} previews={previews} unavailable={unavailable} />;
}
