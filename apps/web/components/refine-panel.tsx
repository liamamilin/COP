"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { useRouter } from "next/navigation";

import {
  acceptCandidatePatch,
  ApiError,
  getCandidatePatchOrNull,
  REFINABLE_KINDS,
  rejectCandidatePatch,
  startGenerationRun,
  type CandidatePatch,
  type DraftEntityKind,
} from "../lib/api";

interface RefinePanelProps {
  projectId: string;
  /** The plural API segment, e.g. "stages". */
  entityKind: DraftEntityKind;
  entityId: string;
  entityTitle: string;
  /** A proposal applies to the active draft; without one there is nowhere to land. */
  hasDraft: boolean;
}

type Stage = "idle" | "generating" | "reviewing" | "done";

/**
 * Ask the model to improve one entity, review the proposal, then accept or
 * reject it.
 *
 * Nothing is written until the user accepts. The proposal is fetched from the
 * run rather than held in component state, so a page reload does not lose the
 * review step, and so a stale proposal is visible as stale instead of quietly
 * applied over newer work.
 */
export function RefinePanel({
  projectId,
  entityKind,
  entityId,
  entityTitle,
  hasDraft,
}: RefinePanelProps) {
  const entityType = REFINABLE_KINDS[entityKind];
  const singular = entityType ?? entityKind.replace(/s$/, "");
  const refunable = entityType !== undefined;
  const router = useRouter();
  const [stage, setStage] = useState<Stage>("idle");
  const [instruction, setInstruction] = useState("");
  const [patch, setPatch] = useState<CandidatePatch | null>(null);
  const [runId, setRunId] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [notice, setNotice] = useState<string | null>(null);
  const pollRef = useRef<ReturnType<typeof setInterval> | null>(null);

  const stopPolling = useCallback(() => {
    if (pollRef.current) clearInterval(pollRef.current);
    pollRef.current = null;
  }, []);

  useEffect(() => stopPolling, [stopPolling]);

  async function start() {
    if (!entityType) {
      setError("This kind of entity cannot be refined.");
      return;
    }
    setError(null);
    setNotice(null);
    setStage("generating");
    setPatch(null);
    try {
      const run = await startGenerationRun(projectId, {
        target: { entity_type: entityType, entity_id: entityId },
        instruction: instruction.trim(),
      });
      setRunId(run.id);
      // The run is queued; poll until a proposal exists. A refinement is short
      // and fires no model calls beyond one, so a tight poll is not wasteful.
      pollRef.current = setInterval(async () => {
        const candidate = await getCandidatePatchOrNull(run.id).catch(() => null);
        if (candidate) {
          stopPolling();
          setPatch(candidate);
          setStage("reviewing");
        }
      }, 1200);
    } catch (cause) {
      setError(cause instanceof ApiError ? cause.message : "The refinement could not start.");
      setStage("idle");
    }
  }

  async function decide(action: "accept" | "reject") {
    if (!runId) return;
    stopPolling();
    setError(null);
    try {
      const result =
        action === "accept" ? await acceptCandidatePatch(runId) : await rejectCandidatePatch(runId);
      setNotice(result.message);
      setStage("done");
      if (action === "accept") {
        // The draft changed underneath this page, so the server data is stale.
        router.refresh();
      }
    } catch (cause) {
      setError(
        cause instanceof ApiError ? cause.message : "That decision could not be recorded.",
      );
      setStage("reviewing");
    }
  }

  async function ensureDraftThenStart() {
    await start();
  }

  if (stage === "reviewing" && patch) {
    const empty = patch.changes.length === 0;
    return (
      <section className="refine-panel" aria-live="polite">
        <header className="refine-header">
          <div>
            <p className="eyebrow">PROPOSED CHANGE</p>
            <h3>{entityTitle || patch.entity_title}</h3>
          </div>
          <button className="secondary-button" onClick={() => setStage("idle")} type="button">
            Dismiss
          </button>
        </header>

        {patch.stale && (
          <p className="refine-warning" role="alert">
            The draft changed after this proposal was made. Accepting it would discard your
            newer edit, so it will be refused.
          </p>
        )}

        {empty ? (
          <p className="refine-empty">
            The model had no change to propose for this {singular}.
            {patch.rejected.length > 0 && " Some proposals were blocked — see below."}
          </p>
        ) : (
          <ul className="refine-diff">
            {patch.changes.map((change) => (
              <li key={change.field}>
                <p className="refine-diff-field">{change.field.replace(/_/g, " ")}</p>
                <p className="refine-diff-before">{change.before || "(empty)"}</p>
                <p className="refine-diff-after">{change.after}</p>
              </li>
            ))}
          </ul>
        )}

        {patch.rejected.length > 0 && (
          <details className="refine-rejected">
            <summary>{patch.rejected.length} proposal(s) were blocked</summary>
            <ul>
              {patch.rejected.map((item, index) => (
                <li key={`${item.field}-${index}`}>
                  <strong>{item.field}</strong> — {item.reason}
                </li>
              ))}
            </ul>
          </details>
        )}

        {error && (
          <p className="form-error" role="alert">
            {error}
          </p>
        )}

        <div className="draft-actions">
          <button
            className="primary-button"
            disabled={empty || patch.stale}
            onClick={() => void decide("accept")}
            type="button"
          >
            Accept into draft
          </button>
          <button className="secondary-button" onClick={() => void decide("reject")} type="button">
            Reject
          </button>
        </div>
        <p className="refine-note">
          Accepting changes the draft only. The published version is untouched.
        </p>
      </section>
    );
  }

  return (
    <section className="refine-panel">
      <header className="refine-header">
        <div>
          <p className="eyebrow">AI REFINEMENT</p>
          <h3>Improve this {singular}</h3>
        </div>
      </header>
      <p className="refine-note">
        The model proposes a change; you see the before and after and decide. Fields you edited
        by hand are protected and cannot be proposed over.
      </p>
      {!hasDraft && (
        <p className="refine-warning" role="alert">
          This project has no active draft, so a proposal would have nowhere to land. Open the
          published version as a draft first, from the version history.
        </p>
      )}

      {!refunable && (
        <p className="refine-warning" role="alert">
          {entityKind.replace(/s$/, "")}s cannot be refined in V1. The model refines Goals, Main
          Processes, and Stages.
        </p>
      )}

      {stage === "generating" ? (
        <p className="refine-empty">Working on a proposal…</p>
      ) : (
        <>
          <label className="draft-field">
            <span>
              What should improve<em>optional</em>
            </span>
            <input
              onChange={(event) => setInstruction(event.target.value)}
              placeholder="Make the outcome verifiable"
              type="text"
              value={instruction}
            />
          </label>
          {error && (
            <p className="form-error" role="alert">
              {error}
            </p>
          )}
          {notice && (
            <p className="draft-saved" role="status">
              {notice}
            </p>
          )}
          <div className="draft-actions">
            <button
              className="primary-button"
              disabled={!hasDraft || !refunable}
              onClick={() => void ensureDraftThenStart()}
              type="button"
            >
              Propose a change
            </button>
          </div>
        </>
      )}
    </section>
  );
}
