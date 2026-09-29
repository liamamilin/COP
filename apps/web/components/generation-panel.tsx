"use client";

import { useCallback, useEffect, useRef, useState } from "react";

import {
  ApiError,
  cancelGenerationRun,
  generationEventsUrl,
  getRunProgress,
  startGenerationRun,
} from "../lib/api";
import {
  describeRunStatus,
  isTerminal,
  type GenerationPhase,
  type GenerationRequest,
  type GenerationRun,
} from "../lib/generation-api";

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
  learnerLevel: "new" | "some_experience" | "advanced";
  depth: "fast" | "standard" | "deep";
  sourceIds: string[];
  /** Shown once a candidate exists, so the user can review before publishing. */
  onCandidateReady: (runId: string) => void;
}

export function GenerationPanel({
  projectId,
  topic,
  scopeHint,
  learnerLevel,
  depth,
  sourceIds,
  onCandidateReady,
}: GenerationPanelProps) {
  const [run, setRun] = useState<GenerationRun | null>(null);
  const [phases, setPhases] = useState<GenerationPhase[]>(PLACEHOLDER_PHASES);
  const [warnings, setWarnings] = useState<string[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [pending, setPending] = useState(false);
  const [webSearch, setWebSearch] = useState(false);
  const [live, setLive] = useState(false);
  const sourceRef = useRef<EventSource | null>(null);
  const lastEventId = useRef<number | undefined>(undefined);

  const teardown = useCallback(() => {
    sourceRef.current?.close();
    sourceRef.current = null;
    setLive(false);
  }, []);

  useEffect(() => teardown, [teardown]);

  // Poll while a run is active. The SSE stream drives the phase list, but a
  // poll is the fallback for when the stream cannot be established (proxies,
  // corporate proxies that buffer, or EventSource being unavailable).
  useEffect(() => {
    if (!run || isTerminal(run.status)) {
      teardown();
      return;
    }
    let cancelled = false;
    const tick = async () => {
      try {
        const progress = await getRunProgress(run.id);
        if (cancelled) return;
        setPhases(progress.phases);
        if (isTerminal(progress.run.status)) {
          setRun(progress.run);
          teardown();
          if (progress.run.status === "completed" || progress.run.status === "needs_attention") {
            onCandidateReady(progress.run.id);
          }
        }
      } catch (cause) {
        // A transient poll failure must not tear down a healthy stream.
        if (!cancelled) setError(describe(cause));
      }
    };
    void tick();
    const timer = setInterval(tick, 1500);
    return () => {
      cancelled = true;
      clearInterval(timer);
    };
  }, [run, teardown, onCandidateReady]);

  function connect(runId: string) {
    teardown();
    if (typeof EventSource === "undefined") return;
    const source = new EventSource(generationEventsUrl(runId, lastEventId.current));
    sourceRef.current = source;
    source.onopen = () => setLive(true);
    source.onmessage = () => {
      // Named events carry the payload; this keeps the connection warm.
    };
    source.addEventListener("step.started", (event) => {
      track(event as MessageEvent<string>);
    });
    source.addEventListener("step.completed", (event) => {
      track(event as MessageEvent<string>);
    });
    source.addEventListener("step.warning", (event) => {
      const data = parse(event as MessageEvent<string>);
      if (Array.isArray(data?.warnings)) {
        setWarnings((current) => [...current, ...(data.warnings as string[])]);
      }
    });
    source.addEventListener("run.started", () => setLive(true));
    source.addEventListener("run.resumed", () => setLive(true));
    for (const type of ["run.completed", "run.failed", "run.cancelled", "run.needs_attention"]) {
      source.addEventListener(type, (event) => {
        const data = parse(event as MessageEvent<string>);
        teardown();
        void refreshRun(runId, data);
      });
    }
    source.onerror = () => {
      // The stream closing is normal when a run finishes; the poll owns the
      // terminal transition so a dropped connection cannot strand the UI.
      setLive(false);
    };
  }

  function track(event: MessageEvent<string>) {
    const data = parse(event);
    if (typeof data?.sequence === "number") lastEventId.current = data.sequence;
  }

  async function refreshRun(runId: string, hint?: unknown) {
    try {
      const progress = await getRunProgress(runId);
      setRun(progress.run);
      setPhases(progress.phases);
      if (progress.run.status === "completed" || progress.run.status === "needs_attention") {
        onCandidateReady(runId);
      }
    } catch (cause) {
      setError(describe(cause));
    }
    if (hint && typeof hint === "object" && "metrics" in hint) {
      setWarnings([]);
    }
  }

  async function start() {
    setError(null);
    setWarnings([]);
    setPending(true);
    setPhases(PLACEHOLDER_PHASES);
    lastEventId.current = undefined;
    const body: GenerationRequest = {
      mode: depth,
      topic,
      scope_hint: scopeHint,
      learner_level: learnerLevel,
      source_ids: sourceIds,
      web_search: webSearch,
    };
    try {
      const created = await startGenerationRun(projectId, body);
      setRun(created);
      connect(created.id);
      void refreshRun(created.id);
    } catch (cause) {
      setError(describe(cause));
    } finally {
      setPending(false);
    }
  }

  async function cancel() {
    if (!run) return;
    setPending(true);
    try {
      const updated = await cancelGenerationRun(run.id);
      setRun(updated);
      setError(null);
    } catch (cause) {
      setError(describe(cause));
    } finally {
      setPending(false);
    }
  }

  const status = run ? describeRunStatus(run) : null;
  const active = run !== null && !isTerminal(run.status);

  return (
    <div className="generation-panel">
      {!run && (
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

          {!active && (
            <button className="secondary-button" onClick={start} type="button">
              {pending ? "Starting…" : "Run again"}
            </button>
          )}
        </section>
      )}
    </div>
  );
}

function parse(event: MessageEvent<string>): Record<string, unknown> | null {
  try {
    const value = JSON.parse(event.data) as unknown;
    return value && typeof value === "object" ? (value as Record<string, unknown>) : null;
  } catch {
    return null;
  }
}

function describe(cause: unknown): string {
  if (cause instanceof ApiError) return cause.message;
  if (cause instanceof Error) return cause.message;
  return "Something went wrong while talking to the API.";
}
