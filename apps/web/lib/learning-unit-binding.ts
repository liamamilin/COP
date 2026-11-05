/** Server-only content binding. This is not an independent semantic review. */
import { createHash } from "node:crypto";

import type { COPArtifact } from "@cop-studio/cop-types";
import type { LearningUnit } from "@cop-studio/cop-types/learning-unit";

export interface UnitManifest {
  checker_version: string;
  scope: string;
  hash_algorithm: string;
  unit_sha256: string;
  artifact_sha256: string;
  issues: { code: string; ref: string; message: string }[];
  not_verified: string[];
}

function canonicalJSON(value: unknown): string {
  if (Array.isArray(value)) return `[${value.map(canonicalJSON).join(",")}]`;
  if (value !== null && typeof value === "object") {
    return `{${Object.entries(value).sort(([a], [b]) => a < b ? -1 : a > b ? 1 : 0)
      .map(([key, child]) => `${JSON.stringify(key)}:${canonicalJSON(child)}`).join(",")}}`;
  }
  return JSON.stringify(value);
}

export function unitContentHash(value: unknown): string {
  return createHash("sha256").update(canonicalJSON(value), "utf8").digest("hex");
}

export function learningUnitBinding(unit: LearningUnit, artifact: COPArtifact, manifest: UnitManifest): boolean {
  return manifest.checker_version === "learning-unit-contract/0.1"
    && manifest.scope === "structure-and-bindings-only"
    && manifest.hash_algorithm === "sha256-canonical-json-v1"
    && manifest.issues.length === 0
    && manifest.artifact_sha256 === unit.binding.artifact_sha256
    && manifest.artifact_sha256 === unitContentHash(artifact)
    && manifest.unit_sha256 === unitContentHash(unit);
}
