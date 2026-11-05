import { isTerminal, type GenerationRun } from "./generation-api";

/**
 * What the generation panel should do when it mounts.
 *
 * Kept out of the component because this is the rule the panel used to get
 * wrong: it assumed a fresh mount meant "no run has ever happened", so leaving
 * the page and coming back offered a new run while one was still working or had
 * already failed. A run lives in the database; the panel only renders a decision
 * made here.
 */
export type ResumeDecision =
  | { kind: "idle" }
  | { kind: "attach"; run: GenerationRun; stream: boolean };

export function decideResume(runs: readonly GenerationRun[]): ResumeDecision {
  const latest = runs[0];
  if (!latest) return { kind: "idle" };
  return { kind: "attach", run: latest, stream: !isTerminal(latest.status) };
}


/**
 * Runs a user can still stop or watch.
 *
 * Exported so a future list view can reuse the same definition of "active"
 * instead of re-deriving it from status strings.
 */
export function activeRun(runs: readonly GenerationRun[]): GenerationRun | undefined {
  return runs.find((run) => !isTerminal(run.status));
}
