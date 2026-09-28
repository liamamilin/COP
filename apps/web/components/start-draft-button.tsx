"use client";

import { useState } from "react";

import { ApiError, createDraftFromVersion } from "../lib/api";

interface StartDraftButtonProps {
  projectId: string;
  versionId: string;
  versionNumber: number;
  /** Present when a draft is already open, which blocks creating another. */
  existingDraftId: string | null;
}

/**
 * Fork a published version into a new editable draft.
 *
 * This is the only way to revise something already live. Published versions
 * have no write endpoint, so "edit v2" means "draft from v2, edit, publish as
 * v3". Without this button the project is a dead end after its first publish.
 */
export function StartDraftButton({
  projectId,
  versionId,
  versionNumber,
  existingDraftId,
}: StartDraftButtonProps) {
  const [pending, setPending] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function start() {
    setPending(true);
    setError(null);
    try {
      await createDraftFromVersion(projectId, versionId);
      // A full document navigation, not `router.push`.
      //
      // `router.push` was tried first and proved unreliable here: the promise
      // resolved while the URL never changed and the in-flight RSC request was
      // aborted, leaving the user on the version history with a draft they
      // could not see. Plain navigation via an anchor is reliable, and the
      // draft editor is a heavy page that benefits from a fresh server render
      // after a mutation anyway.
      window.location.assign(`/projects/${projectId}/draft`);
    } catch (cause) {
      setError(
        cause instanceof ApiError ? cause.message : "The draft could not be created.",
      );
      setPending(false);
    }
  }

  if (existingDraftId) {
    return (
      <a className="secondary-button" href={`/projects/${projectId}/draft`}>
        Open the active draft
      </a>
    );
  }

  return (
    <span className="start-draft">
      <button
        className="primary-button"
        disabled={pending}
        onClick={() => void start()}
        type="button"
      >
        {pending ? "Creating…" : `Draft from v${versionNumber}`}
      </button>
      {error && (
        <span className="form-error" role="alert">
          {error}
        </span>
      )}
    </span>
  );
}
