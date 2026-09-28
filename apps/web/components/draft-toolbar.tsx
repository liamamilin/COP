"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";

import { ApiError, discardDraft, publishDraft } from "../lib/api";
import type { DraftCounts } from "../lib/api";

interface DraftToolbarProps {
  draftId: string;
  counts: DraftCounts;
  hasPublishedVersion: boolean;
}

/**
 * Publish or discard the active draft.
 *
 * Publishing is deliberately a two-step confirm with a required summary: it is
 * the one action in the product that permanently freezes content, and the spec
 * requires it to be an explicit user decision. Discarding asks for a second
 * click too, because the draft may hold edits that were never published.
 */
export function DraftToolbar({ draftId, counts, hasPublishedVersion }: DraftToolbarProps) {
  const router = useRouter();
  const [mode, setMode] = useState<"idle" | "publish" | "discard">("idle");
  const [summary, setSummary] = useState("");
  const [pending, setPending] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const entityCount =
    counts.goals + counts.processes + counts.stages + counts.concepts + counts.operations;

  async function run(action: "publish" | "discard") {
    setPending(true);
    setError(null);
    try {
      if (action === "publish") {
        await publishDraft(draftId, summary);
      } else {
        await discardDraft(draftId);
      }
      router.refresh();
    } catch (cause) {
      setError(cause instanceof ApiError ? cause.message : "That action could not be completed.");
    } finally {
      setPending(false);
    }
  }

  return (
    <section className="draft-toolbar">
      <div className="draft-toolbar-head">
        <div>
          <p className="eyebrow">ACTIVE DRAFT</p>
          <h2>
            {counts.goals} Goals · {counts.processes} Processes · {counts.stages} Stages
          </h2>
          <p className="lead-copy">
            {entityCount} editable entities. Editing changes the draft only;
            {hasPublishedVersion
              ? " the version you published stays exactly as it is."
              : " nothing is published until you choose to."}
          </p>
        </div>
        <div className="draft-toolbar-buttons">
          <button
            className="primary-button"
            onClick={() => {
              setMode("publish");
              setError(null);
            }}
            type="button"
          >
            Publish draft
          </button>
          <button
            className="secondary-button"
            onClick={() => {
              setMode("discard");
              setError(null);
            }}
            type="button"
          >
            Discard draft
          </button>
        </div>
      </div>

      {mode === "publish" && (
        <div className="draft-confirm">
          <label className="draft-field">
            <span>
              What changed in this version<em>optional</em>
            </span>
            <input
              onChange={(event) => setSummary(event.target.value)}
              placeholder="Clarified the tool-calling Stage"
              type="text"
              value={summary}
            />
          </label>
          <p className="draft-confirm-note">
            Publishing freezes this draft as the next version. Later edits start a new draft;
            published versions are never modified.
          </p>
          <div className="draft-actions">
            <button className="primary-button" disabled={pending} onClick={() => void run("publish")} type="button">
              {pending ? "Publishing…" : "Confirm publish"}
            </button>
            <button className="secondary-button" onClick={() => setMode("idle")} type="button">
              Cancel
            </button>
          </div>
        </div>
      )}

      {mode === "discard" && (
        <div className="draft-confirm">
          <p className="draft-confirm-note">
            Discarding throws the draft away, including edits you have not published.
            {hasPublishedVersion
              ? " Your published version is not affected."
              : " You will be left with no COP for this project."}
          </p>
          <div className="draft-actions">
            <button className="danger-button" disabled={pending} onClick={() => void run("discard")} type="button">
              {pending ? "Discarding…" : "Discard the draft"}
            </button>
            <button className="secondary-button" onClick={() => setMode("idle")} type="button">
              Keep editing
            </button>
          </div>
        </div>
      )}

      {error && (
        <p className="form-error" role="alert">
          {error}
        </p>
      )}
    </section>
  );
}
