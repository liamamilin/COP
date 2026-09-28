import { describe, expect, it } from "vitest";

import { DRAFT_EDITABLE_FIELDS } from "../lib/api";
import {
  buildPatch,
  changedFields,
  editableFields,
  ENTITY_LABELS,
  entityCountLabel,
  listEntities,
} from "../lib/draft-editing";
import type { COPArtifact } from "@cop-studio/cop-types";

function artifact(overrides: Partial<COPArtifact> = {}): COPArtifact {
  return {
    schema_version: "0.1",
    artifact_id: "cop.test",
    domain: { name: "Test", scope: "s", target_user: "t", non_goals: [] },
    mental_model: { summary: "m", flow: [] },
    goals: [
      { id: "goal.a", title: "Goal A", outcome: "Outcome A", why_it_matters: "Why A" },
      { id: "goal.b", title: "Goal B", outcome: "Outcome B" },
    ],
    shared_foundations: [],
    main_processes: [
      {
        id: "process.a",
        goal_ref: "goal.a",
        title: "Process A",
        start: { type: "zero", ref: null },
        stage_refs: ["stage.a"],
        outcome: "Process outcome",
      },
    ],
    stages: [
      {
        id: "stage.a",
        title: "Stage A",
        local_goal: "Local goal",
        why_it_exists: "Because",
        local_outcome: "Local outcome",
        concept_refs: [],
        operation_refs: [],
        example: { summary: "An example" },
      },
    ],
    concepts: [
      { id: "concept.a", name: "Concept A", definition: "Def A", role: "Role A" },
    ],
    operations: [{ id: "operation.a", name: "Operation A", definition: "Def A", purpose: "P" }],
    branches: [],
    practices: [],
    expansion_map: [],
    metadata: { language: "en", generated_at: "", generator: "test", source_ids: [] },
    ...overrides,
  } as COPArtifact;
}

describe("editable fields", () => {
  it("exposes only the fields the backend allows", () => {
    const fields = editableFields(artifact(), "goals", "goal.a");
    expect(fields.map((field) => field.name)).toEqual([
      "title",
      "outcome",
      "why_it_matters",
    ]);
  });

  it("never exposes a reference field", () => {
    // `stage_refs` is structure. If it ever appears here, a PATCH could drop a
    // Stage from the main line.
    for (const kind of Object.keys(DRAFT_EDITABLE_FIELDS) as (keyof typeof DRAFT_EDITABLE_FIELDS)[]) {
      for (const field of DRAFT_EDITABLE_FIELDS[kind]) {
        expect(field.endsWith("_ref") || field.endsWith("_refs")).toBe(false);
        expect(field).not.toBe("id");
      }
    }
  });

  it("reads the stage example out of its object shape", () => {
    const fields = editableFields(artifact(), "stages", "stage.a");
    expect(fields.find((field) => field.name === "example")?.value).toBe("An example");
  });

  it("returns nothing for an entity that is not in the artifact", () => {
    expect(editableFields(artifact(), "goals", "goal.missing")).toEqual([]);
  });

  it("uses name as the label for concepts and operations", () => {
    const concept = editableFields(artifact(), "concepts", "concept.a");
    expect(concept[0].label).toBe("Name");
    const operation = editableFields(artifact(), "operations", "operation.a");
    expect(operation[0].label).toBe("Name");
  });
});

describe("required fields", () => {
  it("marks schema-required text as required and the rest as optional", () => {
    const fields = editableFields(artifact(), "goals", "goal.a");
    expect(fields.find((field) => field.name === "title")?.required).toBe(true);
    expect(fields.find((field) => field.name === "why_it_matters")?.required).toBe(false);
  });

  it("requires a stage local_goal, matching the schema", () => {
    const fields = editableFields(artifact(), "stages", "stage.a");
    expect(fields.find((field) => field.name === "local_goal")?.required).toBe(true);
  });
});

describe("build patch", () => {
  it("sends only the fields the user changed", () => {
    const before = editableFields(artifact(), "goals", "goal.a");
    const after = before.map((field) =>
      field.name === "title" ? { ...field, value: "  Renamed  " } : field,
    );
    // The untouched `outcome` must stay out of the body, so a save cannot
    // overwrite content the user did not touch.
    expect(buildPatch(before, after)).toEqual({ title: "Renamed" });
  });

  it("sends an emptied optional field as an explicit empty value", () => {
    const before = editableFields(artifact(), "goals", "goal.a");
    const after = before.map((field) =>
      field.name === "why_it_matters" ? { ...field, value: "" } : field,
    );
    expect(buildPatch(before, after)).toEqual({ why_it_matters: "" });
  });

  it("sends an emptied required field so the backend can reject it", () => {
    // The API owns the "cannot be empty" rule. Dropping the key here would make
    // a cleared required field look unchanged and the save would silently no-op.
    const before = editableFields(artifact(), "goals", "goal.a");
    const after = before.map((field) => ({ ...field, value: "   " }));
    expect(buildPatch(before, after)).toHaveProperty("outcome", "");
  });

  it("sends nothing when nothing changed", () => {
    const before = editableFields(artifact(), "concepts", "concept.a");
    expect(buildPatch(before, before.map((field) => ({ ...field })))).toEqual({});
  });

  it("trims whitespace around saved values", () => {
    const before = editableFields(artifact(), "concepts", "concept.a");
    const after = before.map((field) => ({ ...field, value: "  spaced  " }));
    expect(buildPatch(before, after).definition).toBe("spaced");
  });
});

describe("changed fields", () => {
  it("reports nothing when the form is untouched", () => {
    const fields = editableFields(artifact(), "goals", "goal.a");
    expect(changedFields(fields, fields.map((field) => ({ ...field })))).toEqual([]);
  });

  it("names the fields that differ", () => {
    const before = editableFields(artifact(), "goals", "goal.a");
    const after = before.map((field) =>
      field.name === "outcome" ? { ...field, value: "New outcome" } : field,
    );
    expect(changedFields(before, after)).toEqual(["outcome"]);
  });
});

describe("entity listing", () => {
  it("lists entities with a readable title", () => {
    expect(listEntities(artifact(), "goals")).toEqual([
      { id: "goal.a", title: "Goal A" },
      { id: "goal.b", title: "Goal B" },
    ]);
  });

  it("falls back to name for concepts", () => {
    expect(listEntities(artifact(), "concepts")).toEqual([
      { id: "concept.a", title: "Concept A" },
    ]);
  });

  it("labels processes with the canonical domain name", () => {
    expect(ENTITY_LABELS.processes).toBe("Main Process");
  });
});

describe("section headings", () => {
  it("pluralizes Main Process correctly instead of appending s", () => {
    // Appending "s" to the singular label renders "5 main processs".
    expect(entityCountLabel("processes", 5)).toBe("5 main processes");
  });

  it("uses the singular for a single entity", () => {
    expect(entityCountLabel("processes", 1)).toBe("1 main process");
    expect(entityCountLabel("stages", 1)).toBe("1 stage");
  });

  it("pluralizes every kind without a double s", () => {
    for (const kind of ["goals", "stages", "concepts", "operations"] as const) {
      const label = entityCountLabel(kind, 3);
      expect(label).not.toMatch(/ss\b/);
      expect(label.endsWith("s")).toBe(true);
    }
  });
});
