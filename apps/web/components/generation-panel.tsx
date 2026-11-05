"use client";

import { useEffect, useRef, useState } from "react";

import {
  ApiError,
  cancelGenerationRun,
  getEffectiveGenerationSettings,
  resumeGenerationRun,
  startGenerationRun,
} from "../lib/api";
import {
  describeRunStatus,
  isTerminal,
  type GenerationPhase,
  type GenerationRequest,
} from "../lib/generation-api";
import { useGenerationRun } from "../lib/use-generation-run";

const DEPTH_LABELS = { fast: "Fast", standard: "Standard", deep: "Deep" } as const;
const LEARNER_LABELS = {
  new: "New to domain",
  some_experience: "Some experience",
  advanced: "Advanced",
} as const;
const DETAIL_LABELS = { compact: "Compact", balanced: "Balanced", detailed: "Detailed" } as const;
const EVIDENCE_LABELS = { minimal: "Minimal", key_claims: "Key claims", high: "High" } as const;

/** The generation controls a run inherits, plus the ones it can override. */
export interface EffectiveGeneration {
  language: string;
  generation_depth: "fast" | "standard" | "deep";
  learner_level: "new" | "some_experience" | "advanced";
  detail_density: "compact" | "balanced" | "detailed";
  evidence_density: "minimal" | "key_claims" | "high";
  practice_mode: "priority" | "all" | "off";
}

/** Fallback phase list, used before the first progress poll returns. */
const PLACEHOLDER_PHASES: GenerationPhase[] = [
  { key: "scope", label: "Defining scope", steps: ["H00", "H10"], status: "pending" },
  { key: "sources", label: "Understanding sources", steps: ["H20"], status: "pending" },
  { key: "goals", label: "Finding high-value goals", steps: ["H30"], status: "pending" },
  { key: "processes", label: "Building main processes", steps: ["H40", "H50"], status: "pending" },
  { key: "concepts", label: "Extracting concepts and operations", steps: ["H60"], status: "pending" },
  { key: "compression", label: "Compressing shared foundations", steps: ["H70"], status: "pending" },
  { key: "learning", label: "Generating learning material", steps: ["H80"], status: "pending" },
  { key: "assembly", label: "Assembling the artifact", steps: ["H90"], status: "pending" },
  { key: "quality", label: "Reviewing quality", steps: ["H100", "H110"], status: "pending" },
  { key: "finalize", label: "Finalizing artifact", steps: ["H120", "H130"], status: "pending" },
];

interface GenerationPanelProps {
  projectId: string;
  topic: string;
  scopeHint: string;
  sourceIds: string[];
  /**
   * The settings this run will actually use, already resolved by the backend.
   *
   * Passed in rather than re-derived in the browser: spec `24` §8 puts the merge
   * in the backend, and a client-side copy would be a second implementation that
   * silently drifts. The panel shows these values and lets the user change them
   * for this run only, so what is displayed is what the run was given.
   */
  effective: EffectiveGeneration;
  /** Shown once a candidate exists, so the user can review before publishing. */
  onCandidateReady: (runId: string) => void;
}

export function GenerationPanel({
  projectId,
  topic,
  scopeHint,
  sourceIds,
  effective,
  onCandidateReady,
}: GenerationPanelProps) {
  const { run, progress, restoring, error: observationError, warnings, live, observe } =
    useGenerationRun(projectId, onCandidateReady);
  const phases = progress?.phases ?? PLACEHOLDER_PHASES;
  const recovery = progress?.recovery;
  const [error, setError] = useState<string | null>(null);
  const [pending, setPending] = useState(false);
  const [webSearch, setWebSearch] = useState(false);
  const [resumeTimeout, setResumeTimeout] = useState("");
  const submitting = useRef(false);
  // Run-scoped overrides. Empty means "inherit", which is what keeps the default
  // path identical to no override at all.
  const [overrides, setOverrides] = useState<Partial<EffectiveGeneration>>({});
  // What the backend says the run would get. Never computed here: the panel asks
  // the same endpoint the run uses, so a display value and an executed value
  // cannot drift (spec `24` §8 puts the merge in the backend).
  const [resolved, setResolved] = useState<EffectiveGeneration>(effective);
  const [showOptions, setShowOptions] = useState(false);
  const requestSeq = useRef(0);

  useEffect(() => setResolved(effective), [effective]);

  useEffect(() => {
    if (Object.keys(overrides).length === 0) {
      setResolved(effective);
      return;
    }
    // Sequenced so a slow response for an earlier override cannot land after a
    // newer one and show the user the wrong settings.
    const seq = ++requestSeq.current;
    void getEffectiveGenerationSettings(projectId, { generation: overrides })
      .then((view) => {
        if (seq === requestSeq.current) setResolved(view.effective);
      })
      .catch(() => {
        // Leave the last confirmed values in place rather than guessing; the
        // run itself will fail loudly if the override is rejected.
      });
  }, [projectId, overrides, effective]);

  const isOverridden = (key: keyof EffectiveGeneration) => overrides[key] !== undefined;

  async function start() {
    if (submitting.current) return;
    if (run && !window.confirm("Start a new generation from scratch? This makes new model calls and may incur charges.")) return;
    submitting.current = true;
    setError(null);
    setPending(true);
    // `mode` mirrors `generation_depth` rather than being a second concept: the
    // run previously recorded one value and the Harness read another, so a run's
    // own record could not explain what it actually did.
    const body: GenerationRequest = {
      mode: resolved.generation_depth,
      topic,
      scope_hint: scopeHint,
      learner_level: resolved.learner_level,
      source_ids: sourceIds,
      web_search: webSearch,
      settings_override: { generation: { ...overrides } },
    };
    try {
      const created = await startGenerationRun(projectId, body);
      observe(created);
    } catch (cause) {
      setError(describe(cause));
    } finally {
      submitting.current = false;
      setPending(false);
    }
  }

  async function cancel() {
    if (!run) return;
    setPending(true);
    try {
      const updated = await cancelGenerationRun(run.id);
      observe(updated);
      setError(null);
    } catch (cause) {
      setError(describe(cause));
    } finally {
      setPending(false);
    }
  }

  async function resume() {
    if (!run || !recovery?.allowed || submitting.current) return;
    submitting.current = true;
    setPending(true);
    setError(null);
    try {
      const timeout = resumeTimeout ? Number(resumeTimeout) : undefined;
      if (timeout !== undefined && (!Number.isInteger(timeout) || timeout < 5 || timeout > 600)) {
        throw new Error("Request timeout must be a whole number between 5 and 600 seconds.");
      }
      observe(await resumeGenerationRun(run.id, recovery.attempt, timeout));
    } catch (cause) {
      setError(describe(cause));
    } finally {
      submitting.current = false;
      setPending(false);
    }
  }

  const status = run ? describeRunStatus(run) : null;
  const active = run !== null && !isTerminal(run.status);

  return (
    <div className="generation-panel">
      {observationError && <p className="form-error" role="alert">{observationError}</p>}
      {!run && restoring && (
        <section className="generation-start">
          <p className="muted-note">Checking for an existing run…</p>
        </section>
      )}
      {!run && !restoring && !observationError && (
        <section className="generation-start">
          <div>
            <p className="eyebrow">RUN THE HARNESS</p>
            <h2>Build a COP from this project</h2>
            <p className="lead-copy">
              The Harness turns the topic and attached sources into Goals, Main Processes, and
              Stages. It creates a candidate for you to review; publishing stays your decision.
            </p>
            <label className="generation-search-option">
              <input
                checked={webSearch}
                disabled={pending}
                onChange={(event) => setWebSearch(event.target.checked)}
                type="checkbox"
              />
              <span>
                <strong>Enrich with Exa web research</strong>
                <small>Uses the configured Exa API key and adds bounded web excerpts as sources.</small>
              </span>
            </label>

            <div className="generation-effective">
              <button
                aria-expanded={showOptions}
                className="generation-effective-toggle"
                onClick={() => setShowOptions((value) => !value)}
                type="button"
              >
                {showOptions ? "Hide" : "Adjust"} this run&apos;s settings
                <span className="generation-effective-summary">
                  {DEPTH_LABELS[resolved.generation_depth]} ·{" "}
                  {LEARNER_LABELS[resolved.learner_level]} ·{" "}
                  {DETAIL_LABELS[resolved.detail_density]} ·{" "}
                  {EVIDENCE_LABELS[resolved.evidence_density]}
                </span>
              </button>
              {showOptions && (
                <div className="generation-options">
                  <p className="muted-note">
                    These are the settings this run will use. Change one to override it for this run
                    only; your project defaults are untouched.
                  </p>
                  <label>
                    <span>Language</span>
                    <select
                      onChange={(event) =>
                        setOverrides((current) => ({ ...current, language: event.target.value }))
                      }
                      value={resolved.language}
                    >
                      <option value="auto">Auto</option>
                      <option value="zh-CN">中文</option>
                      <option value="en">English</option>
                      <option value="ja">日本語</option>
                    </select>
                  </label>
                  <label>
                    <span>Depth {isOverridden("generation_depth") ? "(overridden)" : ""}</span>
                    <select
                      onChange={(event) =>
                        setOverrides((current) => ({
                          ...current,
                          generation_depth: event.target
                            .value as EffectiveGeneration["generation_depth"],
                        }))
                      }
                      value={resolved.generation_depth}
                    >
                      <option value="fast">Fast</option>
                      <option value="standard">Standard</option>
                      <option value="deep">Deep</option>
                    </select>
                  </label>
                  <label>
                    <span>Learner level {isOverridden("learner_level") ? "(overridden)" : ""}</span>
                    <select
                      onChange={(event) =>
                        setOverrides((current) => ({
                          ...current,
                          learner_level: event.target
                            .value as EffectiveGeneration["learner_level"],
                        }))
                      }
                      value={resolved.learner_level}
                    >
                      <option value="new">New to domain</option>
                      <option value="some_experience">Some experience</option>
                      <option value="advanced">Advanced</option>
                    </select>
                  </label>
                  <label>
                    <span>Detail density {isOverridden("detail_density") ? "(overridden)" : ""}</span>
                    <select
                      onChange={(event) =>
                        setOverrides((current) => ({
                          ...current,
                          detail_density: event.target
                            .value as EffectiveGeneration["detail_density"],
                        }))
                      }
                      value={resolved.detail_density}
                    >
                      <option value="compact">Compact</option>
                      <option value="balanced">Balanced</option>
                      <option value="detailed">Detailed</option>
                    </select>
                  </label>
                  <label>
                    <span>Evidence {isOverridden("evidence_density") ? "(overridden)" : ""}</span>
                    <select
                      onChange={(event) =>
                        setOverrides((current) => ({
                          ...current,
                          evidence_density: event.target
                            .value as EffectiveGeneration["evidence_density"],
                        }))
                      }
                      value={resolved.evidence_density}
                    >
                      <option value="minimal">Minimal</option>
                      <option value="key_claims">Key claims</option>
                      <option value="high">High</option>
                    </select>
                  </label>
                  <label>
                    <span>Practice {isOverridden("practice_mode") ? "(overridden)" : ""}</span>
                    <select
                      onChange={(event) =>
                        setOverrides((current) => ({
                          ...current,
                          practice_mode: event.target
                            .value as EffectiveGeneration["practice_mode"],
                        }))
                      }
                      value={resolved.practice_mode}
                    >
                      <option value="priority">Priority</option>
                      <option value="all">All processes</option>
                      <option value="off">Off</option>
                    </select>
                  </label>
                  {Object.keys(overrides).length > 0 && (
                    <button onClick={() => setOverrides({})} type="button">
                      Reset to project settings
                    </button>
                  )}
                </div>
              )}
            </div>
          </div>
          <button className="primary-button" disabled={pending} onClick={start} type="button">
            {pending ? "Starting…" : "Generate COP"}
          </button>
          {error && (
            <p className="form-error" role="alert">
              {error}
            </p>
          )}
        </section>
      )}

      {run && (
        <section className="generation-run" aria-live="polite">
          <header className="generation-run-header">
            <div>
              <p className="eyebrow">{status?.headline}</p>
              <p className="lead-copy">{status?.detail}</p>
            </div>
            {active && (
              <button className="secondary-button" disabled={pending} onClick={cancel} type="button">
                {pending ? "Cancelling…" : "Cancel"}
              </button>
            )}
          </header>

          {active && (
            <p className="generation-transport">
              {live ? "Streaming progress" : "Polling for progress"} · {run.status}
            </p>
          )}

          <ol className="phase-list">
            {phases.map((phase) => (
              <li className={`phase ${phase.status}`} key={phase.key}>
                <span className="phase-marker" aria-hidden="true">
                  {phase.status === "done" ? "✓" : phase.status === "active" ? "●" : "○"}
                </span>
                <span className="phase-label">{phase.label}</span>
                <span className="sr-only">{phase.status}</span>
              </li>
            ))}
          </ol>

          {warnings.length > 0 && (
            <details className="generation-warnings">
              <summary>{warnings.length} warning(s) from this run</summary>
              <ul>
                {warnings.map((warning, index) => (
                  <li key={`${index}-${warning}`}>{warning}</li>
                ))}
              </ul>
            </details>
          )}

          {error && (
            <p className="form-error" role="alert">
              {error}
            </p>
          )}

          {run.status === "failed" && recovery?.allowed && (
            <div className="generation-recovery">
              <p className="eyebrow">CHECKPOINT SAVED</p>
              <h3>Continue where you left off.</h3>
              <p className="recovery-summary">
                {recovery.completed_steps.length} steps preserved. Next: {phases.find(
                  (phase) => phase.steps.includes(recovery.from_step ?? ""),
                )?.label ?? recovery.from_step}.
              </p>
              <p className="muted-note">Uses the same model, settings, and sources. Further model calls may incur charges.</p>
              <details className="recovery-options">
                <summary>Adjust request timeout</summary>
                <label><span>Request timeout (seconds)</span>
                  <input type="number" min="5" max="600" value={resumeTimeout}
                    placeholder={String(recovery.timeout_seconds)}
                    onChange={(event) => setResumeTimeout(event.target.value)} disabled={pending} />
                </label>
                <p className="muted-note">Leave blank to keep the current {recovery.timeout_seconds}-second limit.</p>
              </details>
            </div>
          )}
          {run.status === "failed" && recovery && !recovery.allowed && (
            <p className="muted-note">{recovery.reason}</p>
          )}
          {!!recovery?.history.length && (
            <details className="generation-warnings"><summary>Previous attempts ({recovery.history.length})</summary>
              <ul>{recovery.history.map((attempt) => (
                <li key={attempt.attempt}>Attempt {attempt.attempt}: {attempt.error_code} — {attempt.error_message}</li>
              ))}</ul>
            </details>
          )}
          {!active && (
            <div className="generation-actions">
              {run.status === "failed" && recovery?.allowed && (
                <button className="primary-button" disabled={pending} onClick={resume} type="button">
                  {pending ? "Submitting…" : "Resume generation"}
                </button>
              )}
              <button className="secondary-button" disabled={pending} onClick={start} type="button">
                {pending ? "Submitting…" : "Start over"}
              </button>
            </div>
          )}
        </section>
      )}
    </div>
  );
}

function describe(cause: unknown): string {
  if (cause instanceof ApiError) return cause.message;
  if (cause instanceof Error) return cause.message;
  return "Something went wrong while talking to the API.";
}
