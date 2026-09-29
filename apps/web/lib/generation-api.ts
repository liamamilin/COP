export type GenerationRunStatus =
  | "queued"
  | "running"
  | "needs_attention"
  | "completed"
  | "failed"
  | "cancelled";

export type PhaseStatus = "pending" | "active" | "done";

export interface GenerationPhase {
  key: string;
  label: string;
  steps: string[];
  status: PhaseStatus;
}

export interface GenerationRun {
  id: string;
  project_id: string;
  status: GenerationRunStatus;
  requested_mode: string;
  base_version_id: string | null;
  started_at: string | null;
  completed_at: string | null;
  heartbeat_at: string | null;
  worker_id: string | null;
  cancel_requested: boolean;
  error_code: string | null;
  error_message: string | null;
  metrics: Record<string, unknown>;
  created_at: string | null;
  updated_at: string | null;
}

export interface RunProgress {
  run: GenerationRun;
  phases: GenerationPhase[];
  candidate_available: boolean;
}

export interface GenerationCandidate {
  run_id: string;
  status: GenerationRunStatus;
  artifact: unknown;
  warnings: string[];
}

export interface GenerationRequest {
  mode?: "fast" | "standard" | "deep";
  topic?: string;
  scope_hint?: string;
  target_outcomes?: string[];
  learner_level?: "new" | "some_experience" | "advanced";
  source_ids?: string[];
  web_search?: boolean;
  settings_override?: Record<string, unknown>;
  base_version_id?: string | null;
  instruction?: string;
  /**
   * Refine one existing entity instead of generating a whole COP.
   *
   * Omitting this asks for a full generation, so a client that wants a
   * refinement must say which entity it means; there is no "refine whatever
   * seems weakest" mode.
   */
  target?: {
    entity_type: "goal" | "process" | "stage";
    entity_id: string;
  };
}

export interface ApiErrorBody {
  error: { code: string; message: string; details: Record<string, unknown> };
}

const TERMINAL_STATUSES: GenerationRunStatus[] = [
  "completed",
  "needs_attention",
  "failed",
  "cancelled",
];

export function isTerminal(status: GenerationRunStatus): boolean {
  return TERMINAL_STATUSES.includes(status);
}

/**
 * Human-facing copy for a terminal run.
 *
 * Every branch tells the user what happened to their work, because a failed
 * generation must never look like it discarded what they already had.
 */
export function describeRunStatus(run: GenerationRun): {
  headline: string;
  detail: string;
  tone: "ok" | "attention" | "error";
} {
  switch (run.status) {
    case "completed":
      return {
        headline: "Candidate ready",
        detail: "Review it before publishing. Publishing is always your decision.",
        tone: "ok",
      };
    case "needs_attention":
      return {
        headline: "Needs your attention",
        detail:
          run.error_message ??
          "The run kept your work through the last valid checkpoint, but the result still has invalid references. Retry finalization or inspect the run.",
        tone: "attention",
      };
    case "failed":
      return {
        headline: "Generation failed",
        detail:
          run.error_message ??
          "No publishable candidate was produced. Your sources and previous versions are unchanged.",
        tone: "error",
      };
    case "cancelled":
      return {
        headline: "Generation cancelled",
        detail: "Your sources and previous versions are unchanged. You can start again.",
        tone: "error",
      };
    case "running":
      return { headline: "Building your COP", detail: "Progress updates below.", tone: "ok" };
    default:
      return { headline: "Queued", detail: "Waiting for a worker to pick this up.", tone: "ok" };
  }
}

export class ApiError extends Error {
  constructor(
    public readonly status: number,
    public readonly code: string,
    message: string,
  ) {
    super(message);
    this.name = "ApiError";
  }
}
