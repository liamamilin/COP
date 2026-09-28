"use client";

import { useRouter } from "next/navigation";
import { useCallback, useState } from "react";

import { ApiError, createDraftFromRun } from "../lib/api";

import { GenerationPanel } from "./generation-panel";

interface GenerationSectionProps {
  projectId: string;
  topic: string;
  scopeHint: string;
  learnerLevel: "new" | "some_experience" | "advanced";
  depth: "fast" | "standard" | "deep";
  sourceIds: string[];
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

  const handleCandidateReady = useCallback(
    async (runId: string) => {
      try {
        await createDraftFromRun(props.projectId, runId);
        setError(null);
      } catch (cause) {
        // A draft may already exist from an earlier run. That is a normal state,
        // not a failure worth blocking on: the panel already reports the run
        // result, and the draft screen is reachable from the sidebar.
        if (cause instanceof ApiError && cause.status === 409) {
          setError(null);
        } else {
          setError(
            cause instanceof ApiError
              ? cause.message
              : "The candidate is ready, but the draft could not be opened for editing.",
          );
        }
      }
      router.refresh();
    },
    [props.projectId, router],
  );

  return (
    <>
      <GenerationPanel {...props} onCandidateReady={handleCandidateReady} />
      {error && (
        <p className="form-error" role="alert">
          {error}
        </p>
      )}
    </>
  );
}
