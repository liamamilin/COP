import Link from "next/link";

import { DuplicateButton } from "../../../components/duplicate-button";
import { GenerationSection } from "../../../components/generation-section";
import { LearningOverview } from "../../../components/learning-overview";
import type { EffectiveGeneration } from "../../../components/generation-panel";
import { ProjectSetupShell } from "../../../components/project-setup-shell";
import { ProjectShell } from "../../../components/project-shell";
import {
  getEffectiveGenerationSettings,
  getProjectSources,
  getProjectWorkspace,
} from "../../../lib/api";

/**
 * Fallback used only if the settings endpoint is unreachable.
 *
 * These are the built-in defaults, not a guess. The alternative -- hard-coding
 * `depth="standard" learnerLevel="new"` in the component -- is what the audit
 * found: the panel displayed values the backend never received.
 */
const FALLBACK_GENERATION: EffectiveGeneration = {
  language: "auto",
  generation_depth: "standard",
  learner_level: "new",
  detail_density: "balanced",
  evidence_density: "key_claims",
  practice_mode: "priority",
};

export default async function ProjectOverviewPage({
  params,
}: {
  params: Promise<{ projectId: string }>;
}) {
  const { projectId } = await params;
  const { project, version, draft } = await getProjectWorkspace(projectId);

  // Resolved server-side, by the same code path that will resolve it at run
  // time, so the panel's first render already shows the values this project
  // will actually generate with.
  let effectiveGeneration: EffectiveGeneration = FALLBACK_GENERATION;
  try {
    effectiveGeneration = (await getEffectiveGenerationSettings(projectId)).effective;
  } catch {
    // A project with no settings row is normal; the built-in defaults stand.
  }

  if (!version) {
    const sources = await getProjectSources(projectId);
    return (
      <ProjectSetupShell project={project} active="overview" hasDraft={draft !== null}>
        <div className="content-wrap setup-overview">
          <header className="page-header detail-header">
            <p className="eyebrow">{draft ? "DRAFT READY · NOT PUBLISHED" : "PROJECT READY · NO COP YET"}</p>
            <h1>{project.title}</h1>
            <p className="lead-copy">
              {project.scope || "Define the source material and scope for this COP."}
            </p>
          </header>

          {draft && (
            <section className="setup-next-step">
              <span className="step-orbit" aria-hidden="true">✓</span>
              <div>
                <p className="eyebrow">READY FOR REVIEW</p>
                <h2>Your draft is ready.</h2>
                <p>Review and edit your COP. Publishing stays your decision.</p>
              </div>
              <Link className="primary-link" href={`/projects/${projectId}/draft`}>Review draft ↗</Link>
            </section>
          )}

          <section className="setup-next-step">
            <span className="step-orbit">{sources.length}</span>
            <div>
              <p className="eyebrow">SOURCES</p>
              <h2>{sources.length ? "Review your sources" : "Add source material"}</h2>
              <p>
                {sources.length
                  ? `Your ${sources.length} extracted source(s) are ready. Generation can also work from the topic alone.`
                  : "Paste text, upload TXT/Markdown/PDF, or fetch a public URL. Sources are optional."}
              </p>
            </div>
            <Link className="primary-link" href={`/projects/${projectId}/sources`}>
              {sources.length ? "Open sources" : "Add sources"} ↗
            </Link>
          </section>

          <GenerationSection
            effective={effectiveGeneration}
            projectId={projectId}
            scopeHint={project.scope}
            sourceIds={sources.map((source) => source.id)}
            topic={project.domain}
          />
        </div>
      </ProjectSetupShell>
    );
  }
  const artifact = version.artifact;

  return (
    <ProjectShell
      project={project}
      version={version}
      artifact={artifact}
      active="overview"
      hasDraft={draft !== null}
    >
      <div className="content-wrap">
        <LearningOverview artifact={artifact} projectId={projectId} versionId={version.id} title={project.title} />

        <section className="manage-section">
          <div>
            <p className="eyebrow">MANAGE THIS COP</p>
            <h2>Revise it without breaking history</h2>
            <p>
              Published versions are immutable. To change something you draft a copy,
              edit it, and publish it as the next version — so what you believed last
              week stays readable.
            </p>
          </div>
          <div className="manage-actions">
            {draft ? (
              <Link className="primary-link" href={`/projects/${projectId}/draft`}>
                Open the active draft ↗
              </Link>
            ) : (
              <Link className="primary-link" href={`/projects/${projectId}/versions`}>
                Start a new draft from v{version.version_number} ↗
              </Link>
            )}
            <Link className="secondary-button" href={`/projects/${projectId}/versions`}>
              Version history
            </Link>
            <Link className="secondary-button" href={`/projects/${projectId}/sources`}>
              Sources
            </Link>
            {/* Duplicate is a real management action, so it belongs here rather
                than only in Settings where nobody looks. The copy is
                independent: it gets its own sources, versions, and progress. */}
            <DuplicateButton projectId={projectId} />
          </div>
        </section>

      </div>
    </ProjectShell>
  );
}
