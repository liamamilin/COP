import type { COPArtifact } from "@cop-studio/cop-types";

import { DRAFT_EDITABLE_FIELDS, type DraftEntityKind } from "./api";

/**
 * The editable view of one entity, flattened for a form.
 *
 * The artifact is rendered from a version, but a draft needs the same entities
 * as a flat `{field: value}` map. Deriving that here rather than in each
 * component keeps the field list and the backend allowlist in one place.
 */
export type EditableField = {
  name: string;
  label: string;
  value: string;
  multiline: boolean;
  required: boolean;
};

/**
 * Human labels for the editable fields.
 *
 * `example` is stored as an object in the artifact but edited as text, which is
 * why it needs an accessor rather than a plain property read.
 */
const FIELD_LABELS: Record<DraftEntityKind, Record<string, string>> = {
  goals: { title: "Title", outcome: "Outcome", why_it_matters: "Why it matters" },
  processes: { title: "Title", outcome: "Outcome" },
  stages: {
    title: "Title",
    local_goal: "Local goal",
    why_it_exists: "Why this stage exists",
    local_outcome: "Local outcome",
    example: "Example",
  },
  concepts: { name: "Name", definition: "Definition", role: "Role" },
  operations: { name: "Name", definition: "Definition", purpose: "Purpose" },
};

const MULTILINE = new Set([
  "outcome",
  "why_it_matters",
  "local_goal",
  "why_it_exists",
  "local_outcome",
  "example",
  "definition",
  "purpose",
  "summary",
]);

const REQUIRED: Record<DraftEntityKind, readonly string[]> = {
  goals: ["title", "outcome"],
  processes: ["title", "outcome"],
  stages: ["title", "local_goal"],
  concepts: ["name", "definition", "role"],
  operations: ["name", "definition"],
};

export const ENTITY_LABELS: Record<DraftEntityKind, string> = {
  goals: "Goal",
  processes: "Main Process",
  stages: "Stage",
  concepts: "Concept",
  operations: "Operation",
};

function readValue(entity: Record<string, unknown>, field: string): string {
  const raw = entity[field];
  if (field === "example") {
    // The schema types `example` as an object; the editor works on its summary.
    if (!raw || typeof raw !== "object") return "";
    const summary = (raw as Record<string, unknown>).summary;
    return typeof summary === "string" ? summary : "";
  }
  return typeof raw === "string" ? raw : "";
}

function findEntity(
  artifact: COPArtifact,
  kind: DraftEntityKind,
  entityId: string,
): Record<string, unknown> | null {
  const collections: Record<DraftEntityKind, unknown[]> = {
    goals: artifact.goals,
    processes: artifact.main_processes,
    stages: artifact.stages,
    concepts: artifact.concepts,
    operations: artifact.operations,
  };
  const match = collections[kind].find(
    (item) => (item as { id: string }).id === entityId,
  );
  return match ? (match as Record<string, unknown>) : null;
}

export function editableFields(
  artifact: COPArtifact,
  kind: DraftEntityKind,
  entityId: string,
): EditableField[] {
  const entity = findEntity(artifact, kind, entityId);
  if (!entity) return [];
  const required = REQUIRED[kind];
  return DRAFT_EDITABLE_FIELDS[kind].map((name) => ({
    name,
    label: FIELD_LABELS[kind][name] ?? name,
    value: readValue(entity, name),
    multiline: MULTILINE.has(name),
    required: required.includes(name),
  }));
}

/**
 * Build the PATCH body from what actually changed.
 *
 * Only changed fields are sent. Resending every field would be harmless today,
 * but it widens the blast radius of a save: an untouched field could be
 * overwritten by a stale form value. An emptied optional field is sent as an
 * explicit empty string, which is how a user clears content on purpose.
 */
export function buildPatch(
  original: EditableField[],
  current: EditableField[],
): Record<string, string> {
  const before = new Map(original.map((field) => [field.name, field.value]));
  const patch: Record<string, string> = {};
  for (const field of current) {
    if (before.get(field.name) === field.value) continue;
    patch[field.name] = field.value.trim();
  }
  return patch;
}

/** Which fields actually changed, for the "unsaved" indicator. */
export function changedFields(
  original: EditableField[],
  current: EditableField[],
): string[] {
  const before = new Map(original.map((field) => [field.name, field.value]));
  return current
    .filter((field) => before.get(field.name) !== field.value)
    .map((field) => field.name);
}

/** Every entity of a kind, for the draft editor index. */
export function listEntities(
  artifact: COPArtifact,
  kind: DraftEntityKind,
): { id: string; title: string }[] {
  const collections: Record<DraftEntityKind, { id: string; title?: string; name?: string }[]> = {
    goals: artifact.goals,
    processes: artifact.main_processes,
    stages: artifact.stages,
    concepts: artifact.concepts,
    operations: artifact.operations,
  };
  return collections[kind].map((entity) => ({
    id: entity.id,
    title: entity.title ?? entity.name ?? entity.id,
  }));
}
