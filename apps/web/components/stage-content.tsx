/**
 * The one place a Stage's content is rendered.
 *
 * Learn Mode and the Stage page used to render the same fields separately, and
 * had already drifted: Learn showed implementation details inside a collapsed
 * `<details>` and the Stage page showed them nowhere. One component is the fix,
 * because a second renderer is a second thing to forget to update.
 *
 * Props are the artifact and the ids, not a pre-resolved object, so this stays
 * usable from a client component that already holds the artifact (Learn Mode)
 * and from a server component that has just fetched it (Stage page).
 */

import type { COPArtifact, Operation, Stage } from "@cop-studio/cop-types";

import { CopyButton } from "./copy-button";
import { EvidencePanel, type ResolvedSource } from "./evidence-panel";
import { artifactSelectors } from "../lib/artifact-selectors";

/**
 * Renders a command or code block.
 *
 * As text, never as HTML: an implementation detail is model output, and a
 * `<pre>` with children is the only way to show a shell command containing
 * `<`, `>`, or `&` without the browser interpreting it.
 */
function CodeBlock({ label, value }: { label: string; value: string }) {
  const lineCount = value.trimEnd().split("\n").length;
  const code = <pre><code>{value}</code></pre>;
  return (
    <div className="detail-code">
      <div className="detail-code-head">
        <span>{label}</span>
        <CopyButton text={value} />
      </div>
      {lineCount > 30 ? (
        <details className="detail-code-full">
          <summary>Show full code · {lineCount} lines</summary>
          {code}
        </details>
      ) : code}
    </div>
  );
}

export function ImplementationDetail({
  detail,
  index,
}: {
  detail: {
    title?: string;
    action?: string;
    command?: string;
    expected_result?: string;
    caution?: string;
  };
  index: number;
}) {
  return (
    <li className="detail-item">
      <strong>{detail.title || `Step ${index + 1}`}</strong>
      {detail.action && <p>{detail.action}</p>}
      {detail.command && <CodeBlock label="Code / command" value={detail.command} />}
      {detail.expected_result && (
        <p className="detail-expected">
          <span>You should see</span> {detail.expected_result}
        </p>
      )}
      {detail.caution && (
        <p className="detail-caution">
          <span>Watch out</span> {detail.caution}
        </p>
      )}
    </li>
  );
}

export function StageContent({
  artifact,
  stage,
  projectId,
  sources,
  showConcepts = true,
  referenceMode = "project",
}: {
  artifact: COPArtifact;
  stage: Stage;
  projectId: string;
  sources: Record<string, ResolvedSource>;
  showConcepts?: boolean;
  referenceMode?: "project" | "local";
}) {
  const branches = artifactSelectors.getBranchesForStage(artifact, stage);
  const operations: Operation[] = artifactSelectors.getOperationsForStage(artifact, stage);
  const concepts = showConcepts
    ? artifactSelectors.getConceptsForStage(artifact, stage)
    : [];

  // Operation failure modes are the part a beginner needs most and used to be
  // reachable only by opening the Operation page, which nothing linked to from
  // the place they would actually hit the failure.
  const failures = operations.flatMap((operation) =>
    (operation.common_failures ?? []).map((failure) => ({
      operation,
      failure,
    })),
  );

  return (
    <>
      {(stage.implementation_details ?? []).length > 0 && (
        <section className="reading-section">
          <p className="eyebrow">HOW TO DO IT</p>
          <ol className="detail-list">
            {(stage.implementation_details ?? []).map((detail, index) => (
              <ImplementationDetail detail={detail} index={index} key={index} />
            ))}
          </ol>
        </section>
      )}

      {stage.example && (
        <section className="reading-section">
          <p className="eyebrow">EXAMPLE</p>
          <div className="stage-example">
            <p>{stage.example.summary}</p>
            {stage.example.input && (
              <div className="detail-code">
                <div className="detail-code-head">
                  <span>Input</span>
                  <CopyButton text={stage.example.input} />
                </div>
                <pre>
                  <code>{stage.example.input}</code>
                </pre>
              </div>
            )}
            {stage.example.output && (
              <div className="detail-code">
                <div className="detail-code-head">
                  <span>Output</span>
                  <CopyButton text={stage.example.output} />
                </div>
                <pre>
                  <code>{stage.example.output}</code>
                </pre>
              </div>
            )}
            {stage.example.note && <p className="muted-note">{stage.example.note}</p>}
          </div>
        </section>
      )}

      <EvidencePanel refs={stage.evidence_refs} sources={sources} projectId={projectId} referenceMode={referenceMode} />

      {branches.length > 0 && (
        <section className="reading-section">
          <p className="eyebrow">BRANCHES · OPTIONAL PATHS</p>
          {branches.map((branch) => (
            <div className="branch-row" key={branch.id}>
              <span>{branch.type}</span><div><h3>{branch.title}</h3><p>{branch.description}</p></div>
            </div>
          ))}
        </section>
      )}

      {failures.length > 0 && (
        <section className="reading-section">
          <p className="eyebrow">WHEN IT GOES WRONG</p>
          <ul className="failure-list">
            {failures.map(({ operation, failure }) => (
              <li key={`${operation.id}-${failure}`}>
                <span>{failure}</span>
                <a href={referenceMode === "local" ? `#operation-${operation.id}` : `/projects/${projectId}/operations/${encodeURIComponent(operation.id)}`}>
                  {operation.name} ↗
                </a>
              </li>
            ))}
          </ul>
        </section>
      )}

      {concepts.length > 0 && (
        <section className="reading-section">
          <p className="eyebrow">CONCEPTS</p>
          <ul className="concept-inline">
            {concepts.map((concept) => (
              <li key={concept.id}>
                <a href={referenceMode === "local" ? `#concept-${concept.id}` : `/projects/${projectId}/concepts/${encodeURIComponent(concept.id)}`}>
                  {concept.name} ↗
                </a>
                <span>{concept.definition}</span>
              </li>
            ))}
          </ul>
        </section>
      )}
    </>
  );
}
