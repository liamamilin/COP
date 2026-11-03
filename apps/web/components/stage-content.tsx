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
import { stepGuide } from "../lib/learning-guide";

import "./step-guide.css";

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

export function StageExample({ example }: { example: NonNullable<Stage["example"]> }) {
  return (
    <div className="stage-example">
      <p>{example.summary}</p>
      {example.input && <CodeBlock label="Input" value={example.input} />}
      {example.output && <CodeBlock label="Output" value={example.output} />}
      {example.note && <p className="muted-note">{example.note}</p>}
    </div>
  );
}

export function ImplementationDetail({
  detail,
  index,
  showExpectedResult = true,
}: {
  detail: {
    title?: string;
    action?: string;
    command?: string;
    expected_result?: string;
    caution?: string;
  };
  index: number;
  showExpectedResult?: boolean;
}) {
  return (
    <li className="detail-item">
      <strong>{detail.title || `Step ${index + 1}`}</strong>
      {detail.action && <p>{detail.action}</p>}
      {detail.command && <CodeBlock label="Code / command" value={detail.command} />}
      {showExpectedResult && detail.expected_result && (
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
  const guide = stepGuide(stage);
  const context = artifactSelectors.getStageContext(artifact, stage);
  const previous = context.stages[context.index - 1] ?? context.prerequisites.at(-1);
  const next = context.stages[context.index + 1];

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
    <div className="step-guide">
      {previous && <section className="step-handoff" aria-label="Previous step context">
        <p className="eyebrow">COMING FROM THE PREVIOUS STEP</p>
        <strong>{previous.title}</strong>
        {previous.local_outcome && <p>{previous.local_outcome}</p>}
        <small>This is the previous step&apos;s planned result, not confirmation that it has been completed.</small>
      </section>}
      <section className="step-purpose" aria-label="Step purpose">
        <p className="eyebrow">WHAT THIS STEP IS FOR</p>
        <p>{stage.local_goal}</p>
        {stage.why_it_exists && <div className="step-why"><strong>Why this step matters</strong><p>{stage.why_it_exists}</p></div>}
      </section>

      {concepts.length > 0 && <details className="step-primer" open>
        <summary>Understand the ideas used here</summary>
        <dl>{concepts.map((concept) => <div key={concept.id}>
          <dt><a href={referenceMode === "local" ? `#concept-${concept.id}` : `/projects/${projectId}/concepts/${encodeURIComponent(concept.id)}`}>{concept.name} ↗</a></dt>
          <dd><p>{concept.definition || "No explanation is supplied for this concept in the saved plan."}</p>
            {concept.role && <p className="step-concept-role"><strong>Why it matters here</strong> {concept.role}</p>}
          </dd>
        </div>)}</dl>
      </details>}

      <section className="reading-section" data-guide-section="instructions" aria-label="What to do">
        <h3 className="step-section-heading"><span>01</span> What to do</h3>
        {guide.hasCommands && <p className="step-reading-note">Commands are instructions, not execution records. Review them and replace placeholders for your environment before running.</p>}
        {guide.details.length > 0 && (
          <ol className="detail-list">
            {guide.details.map((detail, index) => (
              <ImplementationDetail detail={detail} index={index} key={index} showExpectedResult={false} />
            ))}
          </ol>
        )}
        {!guide.hasInstructions && <p className="step-content-gap">No concrete instructions are supplied in this saved step. Use the explanation and any example as reading material; do not assume a runnable method is present.</p>}
        {stage.example && <details className="step-example">
          <summary>See a worked example</summary>
          <p className="step-reading-note">An illustration from the plan, not a record of your own result.</p>
          <StageExample example={stage.example} />
        </details>}
      </section>

      <section className="reading-section" data-guide-section="checks" aria-label="Check your result">
        <h3 className="step-section-heading"><span>02</span> Check your result</h3>
        {stage.local_outcome && <div className="step-target"><span>Expected outcome</span><p>{stage.local_outcome}</p></div>}
        {guide.checks.length > 0 ? <ul className="step-checks">{guide.checks.map((check) => <li key={check.index}>
          <strong>{check.title}</strong><p>{check.text}</p>
        </li>)}</ul> : <p className="step-content-gap">No explicit check is supplied in this saved step. An expected outcome or an example alone does not verify success.</p>}
        {guide.checks.length > 0 && guide.uncheckedActions > 0 && <p className="step-content-gap">Some actions have no explicit check in the saved plan. The checks above do not verify every action.</p>}
        <p className="step-reading-note">Compare these targets with your own result before marking the step complete. Completion is self-reported, not independently verified by COP.</p>
        {next && <div className="step-next-context"><strong>Where this leads</strong><p>{next.title}</p><p>{next.local_goal}</p></div>}
      </section>

      {(guide.cautions.length > 0 || failures.length > 0) && <details className="step-help" data-guide-section="troubleshooting">
        <summary>If you get stuck</summary>
        <p className="eyebrow">WHEN IT GOES WRONG</p>
        {guide.cautions.length > 0 && <p className="step-reading-note">Review the cautions shown next to the action you attempted.</p>}
        {failures.length > 0 && <ul className="failure-list">
          {failures.map(({ operation, failure }) => <li key={`${operation.id}-${failure}`}>
            <span>{failure}</span>
            <a href={referenceMode === "local" ? `#operation-${operation.id}` : `/projects/${projectId}/operations/${encodeURIComponent(operation.id)}`}>{operation.name} ↗</a>
          </li>)}
        </ul>}
      </details>}

      <details className="step-reference" data-guide-section="background">
        <summary>Terms, sources &amp; optional paths</summary>
        {operations.length > 0 && <section className="reading-section">
          <p className="eyebrow">OPERATIONS</p>
          <ul className="concept-inline">{operations.map((operation) => <li key={operation.id}>
            <a href={referenceMode === "local" ? `#operation-${operation.id}` : `/projects/${projectId}/operations/${encodeURIComponent(operation.id)}`}>{operation.name} ↗</a>
            <span>{operation.definition}</span>
          </li>)}</ul>
        </section>}
        <EvidencePanel refs={stage.evidence_refs} sources={sources} projectId={projectId} referenceMode={referenceMode} />
        {branches.length > 0 && <section className="reading-section">
          <p className="eyebrow">BRANCHES · OPTIONAL PATHS</p>
          {branches.map((branch) => (
            <div className="branch-row" key={branch.id}>
              <span>{branch.type}</span><div><h3>{branch.title}</h3><p>{branch.description}</p></div>
            </div>
          ))}
        </section>}
      </details>
    </div>
  );
}
