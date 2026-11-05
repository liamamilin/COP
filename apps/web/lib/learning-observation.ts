/** Local-only self-reports. No progress transport, automatic grading or code execution. */
import type { LearningUnit } from "@cop-studio/cop-types/learning-unit";

export interface QuestionResponse {
  answer: string;
  help_used: string;
  hints_revealed: number;
  criteria_revealed: boolean;
}
export interface PathObservation {
  responses: Record<string, QuestionResponse>;
  observations: Record<string, string>;
}
export interface LearningObservation {
  format: "cop-learning-observation/0.1";
  scope: "unverified-self-report";
  unit_id: string;
  unit_sha256: string;
  artifact_sha256: string;
  active_path_id: string;
  updated_at: string;
  paths: Record<string, PathObservation>;
}

export const emptyResponse = (): QuestionResponse => ({
  answer: "", help_used: "", hints_revealed: 0, criteria_revealed: false,
});
export const appliesToPath = (ids: string[], pathId: string) => ids.length === 0 || ids.includes(pathId);
export const observationKey = (unitId: string) => `cop:learning-observation:${unitId}`;

export function newObservation(unit: LearningUnit, unitHash: string): LearningObservation {
  return {
    format: "cop-learning-observation/0.1", scope: "unverified-self-report",
    unit_id: unit.unit_id, unit_sha256: unitHash, artifact_sha256: unit.binding.artifact_sha256,
    active_path_id: unit.paths[0].id, updated_at: new Date().toISOString(),
    paths: Object.fromEntries(unit.paths.map((path) => [path.id, { responses: {}, observations: {} }])),
  };
}

function object(value: unknown): value is Record<string, unknown> {
  return value !== null && typeof value === "object" && !Array.isArray(value);
}
function keys(value: Record<string, unknown>, allowed: string[]) {
  return Object.keys(value).every((key) => allowed.includes(key));
}
function text(value: unknown): value is string { return typeof value === "string" && value.length <= 12000; }

/** Validate at the storage boundary; reject stale or malformed notes, never migrate silently. */
export function parseObservation(raw: string, unit: LearningUnit, hash: string): LearningObservation {
  if (raw.length > 200000) throw new Error("The notes file is too large.");
  const value: unknown = JSON.parse(raw);
  if (!object(value) || !keys(value, ["format", "scope", "unit_id", "unit_sha256", "artifact_sha256", "active_path_id", "updated_at", "paths"])
    || value.format !== "cop-learning-observation/0.1" || value.scope !== "unverified-self-report"
    || value.unit_id !== unit.unit_id || value.unit_sha256 !== hash
    || value.artifact_sha256 !== unit.binding.artifact_sha256) {
    throw new Error("These notes belong to a different lesson revision or format.");
  }
  const pathIds = unit.paths.map((path) => path.id);
  if (typeof value.active_path_id !== "string" || !pathIds.includes(value.active_path_id)
    || typeof value.updated_at !== "string" || !Number.isFinite(Date.parse(value.updated_at))
    || !object(value.paths) || !keys(value.paths, pathIds) || Object.keys(value.paths).length !== pathIds.length) {
    throw new Error("The notes have an invalid path or timestamp.");
  }
  const questions = [...unit.steps.map((step) => step.practice), ...unit.assessment];
  for (const pathId of pathIds) {
    const path = value.paths[pathId];
    if (!object(path) || !keys(path, ["responses", "observations"]) || !object(path.responses) || !object(path.observations)
      || !keys(path.observations, unit.steps.map((step) => step.stage_ref))
      || Object.values(path.observations).some((item) => !text(item))) throw new Error("The step observations are invalid.");
    for (const [id, response] of Object.entries(path.responses)) {
      const question = questions.find((item) => item.id === id && appliesToPath(item.path_ids, pathId));
      if (!question || !object(response) || !keys(response, ["answer", "help_used", "hints_revealed", "criteria_revealed"])
        || !text(response.answer) || !text(response.help_used)
        || typeof response.hints_revealed !== "number" || !Number.isInteger(response.hints_revealed)
        || response.hints_revealed < 0 || response.hints_revealed > question.hints.length
        || typeof response.criteria_revealed !== "boolean") throw new Error("A question response is invalid.");
    }
  }
  return value as unknown as LearningObservation;
}

export function exportObservation(value: LearningObservation): string {
  return JSON.stringify({ ...value, updated_at: new Date().toISOString() }, null, 2) + "\n";
}
