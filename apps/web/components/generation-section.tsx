"use client";

import { useRouter } from "next/navigation";
import { useCallback, useEffect, useRef, useState } from "react";

import { prepareGenerationDraft } from "../lib/generation-draft";

import { GenerationPanel, type EffectiveGeneration } from "./generation-panel";

interface GenerationSectionProps {
  projectId: string;
  topic: string;
  scopeHint: string;
  sourceIds: string[];
  /**
   * Resolved by the backend from run > project > app > built-in. Passed through
   * untouched: the browser must not own the merge (spec `24` §8), and a second
   * implementation of precedence would drift from the one that actually runs.
   */
  effective: EffectiveGeneration;
}

/**
 * Client wrapper that revalidates the server-rendered project page once a
 * candidate exists, so the overview switches from setup mode to the workspace
 * without the user having to reload by hand.
 *
 * A completed run also becomes the project's draft. The run already produced and
 * validated the artifact, and creating the draft here is what makes it editable;
 * it still does not publish, which stays a separate explicit action.
 */
export function GenerationSection(props: GenerationSectionProps) {
  const router = useRouter();
  const [error, setError] = useState<string | null>(null);
  const [ready, setReady] = useState<{ matchesRun: boolean } | null>(null);
  const [failedRunId, setFailedRunId] = useState<string | null>(null);
  const [opening, setOpening] = useState(false);
  const resultRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (ready) resultRef.current?.scrollIntoView({ block: "nearest" });
  }, [ready]);

  const handleCandidateReady = useCallback(
    async (runId: string) => {
      setOpening(true);
      try {
        const result = await prepareGenerationDraft(props.projectId, runId);
        setReady({ matchesRun: result.matchesRun });
        setError(null);
        setFailedRunId(null);
        router.refresh();
      } catch (cause) {
        setFailedRunId(runId);
        setError(cause instanceof Error ? cause.message : "The candidate is ready, but its draft could not be opened.");
      } finally {
        setOpening(false);
      }
    },
    [props.projectId, router],
  );

  return (
    <>
      <GenerationPanel {...props} onCandidateReady={handleCandidateReady} />
      {ready && (
        <div className="generation-result" ref={resultRef} role="status">
          <p className="eyebrow">{ready.matchesRun ? "READY FOR REVIEW" : "EXISTING DRAFT"}</p>
          <h2>{ready.matchesRun ? "Your draft is ready." : "An earlier draft is still open."}</h2>
          <p>{ready.matchesRun
            ? "Review your generated COP and make any edits. Publish only when you are ready."
            : "The new candidate is saved. Your existing draft and edits have not been replaced."}</p>
          <a className="primary-link" href={`/projects/${props.projectId}/draft`}>
            {ready.matchesRun ? "Review draft" : "Review existing draft"} ↗
          </a>
        </div>
      )}
      {opening && <p className="muted-note" role="status">Preparing your draft…</p>}
      {error && (
        <p className="form-error" role="alert">
          {error}
        </p>
      )}
      {failedRunId && (
        <button className="secondary-button" type="button" disabled={opening}
          onClick={() => void handleCandidateReady(failedRunId)}>
          {opening ? "Opening…" : "Retry opening draft"}
        </button>
      )}
    </>
  );
}
