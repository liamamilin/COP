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

export interface VersionSummary {
  id: string;
  project_id: string;
  version_number: number;
  /** Null for the first published version; set on every later one. */
  parent_version_id: string | null;
  run_id: string | null;
  change_summary: string;
  created_by: "user" | "harness" | "mixed";
  created_at: string;
}

export interface VersionDetail extends VersionSummary {
  artifact: COPArtifact;
}

export interface DraftCounts {
  goals: number;
  processes: number;
  stages: number;
  concepts: number;
  operations: number;
  shared_foundations: number;
  practices: number;
}

export interface DraftSummary {
  id: string;
  project_id: string;
  base_version_id: string | null;
  source_run_id: string | null;
  updated_at: string;
  title: string;
  counts: DraftCounts;
}

export interface DraftDetail extends DraftSummary {
  artifact: COPArtifact;
}

/** API path segment -> editable field names, mirroring backend `EDITABLE_FIELDS`. */
export const DRAFT_EDITABLE_FIELDS = {
  goals: ["title", "outcome", "why_it_matters"],
  processes: ["title", "outcome"],
  stages: ["title", "local_goal", "why_it_exists", "local_outcome", "example"],
  concepts: ["name", "definition", "role"],
  operations: ["name", "definition", "purpose"],
} as const satisfies Record<string, readonly string[]>;

export type DraftEntityKind = keyof typeof DRAFT_EDITABLE_FIELDS;

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

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${baseUrl()}${path}`, { cache: "no-store", ...init });
  if (!response.ok) {
    throw await errorFrom(response, path);
  }
  if (response.status === 204) return undefined as T;
  return (await response.json()) as T;
}

/** Server-rendered reads stay on the internal URL; writes go to the public one. */
async function post<T>(path: string, body?: unknown): Promise<T> {
  return send<T>(path, { method: "POST", body: body === undefined ? undefined : JSON.stringify(body) });
}

async function send<T>(path: string, init: RequestInit): Promise<T> {
  const response = await fetch(`${publicApiBaseUrl()}${path}`, {
    ...init,
    headers: init.body ? { "Content-Type": "application/json", ...init.headers } : init.headers,
  });
  if (!response.ok) {
    throw await errorFrom(response, path);
  }
  if (response.status === 204) return undefined as T;
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

export function getVersions(projectId: string): Promise<VersionSummary[]> {
  return request<VersionSummary[]>(`/projects/${encodeURIComponent(projectId)}/versions`);
}

/**
 * The project's active draft, or null when there is none.
 *
 * A 404 is an ordinary state here, not a failure: most of the time a project has
 * no draft, so this must not throw or every page would need a try/catch.
 */
export async function getDraft(projectId: string): Promise<DraftDetail | null> {
  try {
    return await request<DraftDetail>(`/projects/${encodeURIComponent(projectId)}/draft`);
  } catch (error) {
    if (error instanceof ApiError && error.status === 404) return null;
    throw error;
  }
}

export function createDraftFromRun(projectId: string, runId: string): Promise<DraftDetail> {
  return post<DraftDetail>(
    `/projects/${encodeURIComponent(projectId)}/drafts/from-run/${encodeURIComponent(runId)}`,
  );
}

export function createDraftFromVersion(
  projectId: string,
  versionId: string,
): Promise<DraftDetail> {
  return post<DraftDetail>(
    `/projects/${encodeURIComponent(projectId)}/drafts/from-version/${encodeURIComponent(versionId)}`,
  );
}

export function publishDraft(draftId: string, changeSummary: string): Promise<VersionSummary> {
  return post<VersionSummary>(`/drafts/${encodeURIComponent(draftId)}/publish`, {
    change_summary: changeSummary,
  });
}

export function discardDraft(draftId: string): Promise<void> {
  return request<void>(`/drafts/${encodeURIComponent(draftId)}`, { method: "DELETE" });
}

export function patchDraftEntity(
  draftId: string,
  kind: DraftEntityKind,
  entityId: string,
  changes: Record<string, string>,
): Promise<DraftSummary> {
  return send<DraftSummary>(
    `/drafts/${encodeURIComponent(draftId)}/${kind}/${encodeURIComponent(entityId)}`,
    { method: "PATCH", body: JSON.stringify(changes) },
  );
}

export function patchDraftMetadata(
  draftId: string,
  changes: Record<string, unknown>,
): Promise<DraftSummary> {
  return send<DraftSummary>(`/drafts/${encodeURIComponent(draftId)}/metadata`, {
    method: "PATCH",
    body: JSON.stringify(changes),
  });
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
  return post<GenerationRun>(
    `/projects/${encodeURIComponent(projectId)}/generation-runs`,
    body,
  );
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
  return post<GenerationRun>(`/generation-runs/${encodeURIComponent(runId)}/cancel`);
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

/**
 * Project, latest published version, and the active draft if one exists.
 *
 * The draft is optional, so the version fetch is allowed to 404 as well: a
 * project with neither a version nor a draft is the pre-M4 setup state.
 */
export async function getProjectWorkspace(projectId: string) {
  const project = await getProject(projectId);
  const [version, draft] = await Promise.all([
    getLatestVersion(projectId).catch((error: unknown) => {
      if (error instanceof ApiError && error.status === 404) return null;
      throw error;
    }),
    getDraft(projectId),
  ]);
  return { project, version, draft, artifact: version?.artifact ?? null };
}
