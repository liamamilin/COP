import type { COPArtifact } from "@cop-studio/cop-types";

import type {
  GenerationRequest,
  GenerationRun,
  RunProgress,
} from "./generation-api";

export interface ProjectSummary {
  id: string;
  title: string;
  description: string;
  domain: string;
  scope: string;
  preferred_language: string;
  status: "active" | "archived" | "deleted";
  created_at: string;
  updated_at: string;
  latest_version: number | null;
}

export interface VersionDetail {
  id: string;
  project_id: string;
  version_number: number;
  change_summary: string;
  created_by: "user" | "harness" | "mixed";
  created_at: string;
  artifact: COPArtifact;
}

export interface SourceSummary {
  id: string;
  project_id: string;
  type: "text" | "txt" | "markdown" | "pdf" | "url";
  title: string;
  original_uri: string | null;
  status: "created" | "processing" | "ready" | "failed";
  metadata: Record<string, unknown>;
  char_count: number | null;
  preview: string | null;
  created_at: string;
  updated_at: string;
}

export interface AppSettings {
  provider: {
    type: "mock" | "openai_compatible";
    base_url: string;
    model: string;
    timeout: number;
    max_retries: number;
    mock_scenario: "success" | "invalid" | "timeout" | "rate_limit" | "slow";
    has_api_key: boolean;
    api_key_hint: string | null;
  };
  generation: {
    language: string;
    generation_depth: "fast" | "standard" | "deep";
    learner_level: "new" | "some_experience" | "advanced";
    detail_density: "compact" | "balanced" | "detailed";
    practice_mode: "off" | "priority" | "all";
    evidence_density: "minimal" | "key_claims" | "high";
  };
  appearance: { theme: "system" | "light" | "dark"; density: "comfortable" | "compact" };
}

export class ApiError extends Error {
  constructor(
    public readonly status: number,
    message: string,
  ) {
    super(message);
  }
}

async function errorFrom(response: Response, path: string): Promise<ApiError> {
  const payload = (await response.json().catch(() => null)) as
    | { detail?: string; error?: { code: string; message: string } }
    | null;
  if (payload?.error?.message) {
    return new ApiError(response.status, payload.error.message);
  }
  if (typeof payload?.detail === "string") {
    return new ApiError(response.status, payload.detail);
  }
  return new ApiError(response.status, `COP Studio API returned ${response.status} for ${path}`);
}

function baseUrl(): string {
  return (
    process.env.INTERNAL_API_BASE_URL ??
    process.env.NEXT_PUBLIC_API_BASE_URL ??
    "http://localhost:8000/api/v1"
  );
}

async function request<T>(path: string): Promise<T> {
  const response = await fetch(`${baseUrl()}${path}`, { cache: "no-store" });
  if (!response.ok) {
    throw await errorFrom(response, path);
  }
  return (await response.json()) as T;
}

export function getProjects(): Promise<ProjectSummary[]> {
  return request<ProjectSummary[]>("/projects");
}

export function getProject(projectId: string): Promise<ProjectSummary> {
  return request<ProjectSummary>(`/projects/${encodeURIComponent(projectId)}`);
}

export function getLatestVersion(projectId: string): Promise<VersionDetail> {
  return request<VersionDetail>(
    `/projects/${encodeURIComponent(projectId)}/versions/latest`,
  );
}

export function getProjectSources(projectId: string): Promise<SourceSummary[]> {
  return request<SourceSummary[]>(`/projects/${encodeURIComponent(projectId)}/sources`);
}

export function getAppSettings(): Promise<AppSettings> {
  return request<AppSettings>("/settings");
}

export function publicApiBaseUrl(): string {
  return process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000/api/v1";
}

export async function startGenerationRun(
  projectId: string,
  body: GenerationRequest,
): Promise<GenerationRun> {
  const response = await fetch(
    `${publicApiBaseUrl()}/projects/${encodeURIComponent(projectId)}/generation-runs`,
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    },
  );
  if (!response.ok) throw await errorFrom(response, "/generation-runs");
  return (await response.json()) as GenerationRun;
}

export async function getGenerationRun(runId: string): Promise<GenerationRun> {
  return request<GenerationRun>(
    `/generation-runs/${encodeURIComponent(runId)}`,
  );
}

export async function getRunProgress(runId: string): Promise<RunProgress> {
  return request<RunProgress>(
    `/generation-runs/${encodeURIComponent(runId)}/progress`,
  );
}

export async function cancelGenerationRun(runId: string): Promise<GenerationRun> {
  const response = await fetch(
    `${publicApiBaseUrl()}/generation-runs/${encodeURIComponent(runId)}/cancel`,
    { method: "POST" },
  );
  if (!response.ok) throw await errorFrom(response, "/cancel");
  return (await response.json()) as GenerationRun;
}

/**
 * URL of the SSE progress stream.
 *
 * EventSource cannot send custom headers, so `Last-Event-ID` is passed as a
 * query parameter; the server accepts either form on reconnect.
 */
export function generationEventsUrl(runId: string, lastEventId?: number): string {
  const base = `${publicApiBaseUrl()}/generation-runs/${encodeURIComponent(runId)}/events`;
  return lastEventId === undefined ? base : `${base}?last_event_id=${lastEventId}`;
}

export async function getWorkspace(projectId: string) {
  const [project, version] = await Promise.all([
    getProject(projectId),
    getLatestVersion(projectId),
  ]);
  return { project, version, artifact: version.artifact };
}
