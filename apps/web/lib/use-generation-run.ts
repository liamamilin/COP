"use client";

import { useCallback, useEffect, useRef, useState } from "react";

import { generationEventsUrl, getRunProgress, listGenerationRuns } from "./api";
import { isTerminal, type GenerationRun, type RunProgress } from "./generation-api";
import { decideResume } from "./run-resume";

/** Owns observation, not execution: mounting/reconnecting never starts a paid run. */
export function useGenerationRun(projectId: string, onCandidateReady: (id: string) => void) {
  const [run, setRun] = useState<GenerationRun | null>(null);
  const [progress, setProgress] = useState<RunProgress | null>(null);
  const [restoring, setRestoring] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [live, setLive] = useState(false);
  const [warnings, setWarnings] = useState<string[]>([]);
  const observed = useRef<string | null>(null);
  const revision = useRef(0);
  const cursor = useRef(0);
  const notified = useRef(new Set<string>());

  const refresh = useCallback(async (id: string) => {
    const version = revision.current;
    const next = await getRunProgress(id);
    if (observed.current !== id || version !== revision.current) return;
    if ((next.last_event_id ?? 0) < cursor.current) return;
    cursor.current = Math.max(cursor.current, next.last_event_id ?? 0);
    setRun(next.run);
    setProgress(next);
  }, []);

  const observe = useCallback((next: GenerationRun) => {
    revision.current += 1;
    observed.current = next.id;
    cursor.current = 0;
    setProgress(null);
    setWarnings([]);
    setError(null);
    setRun(next);
    void refresh(next.id).catch((e: Error) => setError(e.message));
  }, [refresh]);

  useEffect(() => {
    let disposed = false;
    setRestoring(true);
    observed.current = null;
    revision.current += 1;
    setRun(null);
    setProgress(null);
    setError(null);
    void listGenerationRuns(projectId).then(async (runs) => {
      if (disposed) return;
      const decision = decideResume(runs);
      if (decision.kind === "attach") {
        observed.current = decision.run.id;
        cursor.current = 0;
        await refresh(decision.run.id);
      }
    }).catch((e: Error) => {
      if (!disposed) setError(`Could not restore the generation history: ${e.message}. Refresh to try again.`);
    }).finally(() => {
      if (!disposed) setRestoring(false);
    });
    return () => { disposed = true; observed.current = null; revision.current += 1; };
  }, [projectId, refresh]);

  useEffect(() => {
    if (!progress?.candidate_available || !isTerminal(progress.run.status)) return;
    const key = `${progress.run.id}:${progress.recovery?.attempt ?? 1}`;
    if (notified.current.has(key)) return;
    notified.current.add(key);
    onCandidateReady(progress.run.id);
  }, [progress, onCandidateReady]);

  const id = run?.id;
  const active = !!run && !isTerminal(run.status);
  const attempt = progress?.recovery?.attempt;
  useEffect(() => {
    if (!id || !active) { setLive(false); return; }
    let disposed = false;
    let polling = false;
    const tick = async () => {
      if (disposed || polling) return;
      polling = true;
      try { await refresh(id); }
      catch (e) { if (!disposed) setError((e as Error).message); }
      finally { polling = false; }
    };
    let source: EventSource | null = null;
    try {
      if (typeof EventSource !== "undefined") source = new EventSource(generationEventsUrl(id, cursor.current));
    } catch {
      // An unsupported or blocked transport must not prevent polling.
      setLive(false);
    }
    if (source) {
      source.onopen = () => { if (!disposed) setLive(true); };
      source.onerror = () => { if (!disposed) setLive(false); };
      for (const type of ["step.completed", "run.completed", "run.failed", "run.cancelled", "run.needs_attention"]) {
        // SSE is only a hint. The current DB status, not an old terminal event,
        // decides whether the observer closes or opens the candidate.
        source.addEventListener(type, () => { void tick(); });
      }
      source.addEventListener("step.warning", (event) => {
        try {
          const data = JSON.parse((event as MessageEvent<string>).data);
          if (!disposed && Array.isArray(data.warnings)) setWarnings(data.warnings);
        } catch { /* A malformed hint must not stop polling. */ }
      });
    }
    void tick();
    const timer = setInterval(() => { void tick(); }, 1500);
    return () => { disposed = true; source?.close(); clearInterval(timer); };
  }, [id, active, attempt, refresh]);

  return { run, progress, restoring, error, live, warnings, observe };
}
