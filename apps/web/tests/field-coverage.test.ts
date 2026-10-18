/**
 * R0 — which artifact fields have a user entry point.
 *
 * The backend can hold a field that no screen ever renders and no form ever
 * edits. That is not a bug the type system catches, and it is exactly how this
 * product ended up with a COP whose 22 Stages carried no example and no
 * implementation detail: the data existed in the model, the mock even produced
 * it, and no user could reach it.
 *
 * "Present in the JSON" is not "delivered to the user". These tests make the
 * second claim checkable.
 *
 * How a surface is detected: by the field name appearing in a page or component
 * under `app/` or `components/`. That is a source-level check on purpose. The
 * vitest environment is `node`, so there is no DOM to render into, and asserting
 * on a string that must be rendered is a stronger statement than asserting on
 * one that happens to be, because it also fails if the field is read and then
 * discarded.
 */

import { readFileSync, readdirSync, statSync } from "node:fs";
import { join, relative } from "node:path";
import { fileURLToPath } from "node:url";

import { describe, expect, it } from "vitest";

import { DRAFT_EDITABLE_FIELDS } from "../lib/api";

const WEB_ROOT = fileURLToPath(new URL("..", import.meta.url));

function sourceFiles(dir: string): string[] {
  const found: string[] = [];
  for (const entry of readdirSync(dir)) {
    const full = join(dir, entry);
    if (statSync(full).isDirectory()) {
      // node_modules and build output are not user surfaces.
      if (entry === "node_modules" || entry === ".next") continue;
      found.push(...sourceFiles(full));
    } else if (/\.tsx?$/.test(entry)) {
      found.push(full);
    }
  }
  return found;
}

const APP_ROOT = join(WEB_ROOT, "app");
const COMPONENT_ROOT = join(WEB_ROOT, "components");
const SURFACES = [...sourceFiles(APP_ROOT), ...sourceFiles(COMPONENT_ROOT)].map(
  (path) => ({ path, name: relative(WEB_ROOT, path), text: readFileSync(path, "utf8") }),
);

/** Every surface that mentions a field, for a failure message worth reading. */
function surfacesMentioning(field: string): string[] {
  return SURFACES.filter((surface) => surface.text.includes(field)).map((surface) => surface.name);
}

type Requirement = { field: string; why: string; batch: string };

/**
 * A field the user must be able to read somewhere in the product.
 *
 * Listed in the order a learner meets them, because that is the order the
 * failure hurts in.
 */
const MUST_BE_READABLE: Requirement[] = [
  {
    field: "local_goal",
    why: "the Stage's own purpose, the spine of the Main Process",
    batch: "shipped",
  },
  {
    field: "why_it_exists",
    why: "why this Stage is in the main line at all",
    batch: "shipped",
  },
  {
    field: "example",
    why: "a reader needs to see the finished result before the steps",
    batch: "R1/R4",
  },
  {
    field: "implementation_details",
    why: "a Stage that names Operations but gives no method is not executable",
    batch: "R1/R4",
  },
  {
    field: "common_failures",
    why: "where a beginner goes wrong, and what to do about it",
    batch: "R4",
  },
  {
    field: "non_goals",
    why: "scope boundaries; a domain without them reads as an encyclopedia",
    batch: "R4",
  },
  {
    field: "prerequisite_goal_refs",
    why: "the Goal's position in the order, which Learn Mode depends on",
    batch: "R4",
  },
  {
    field: "evidence_refs",
    why: "a citation the user cannot open is a claim they must take on faith",
    batch: "R3/R4",
  },
  {
    field: "checkpoint_questions",
    why: "the questions that make a Practice completable rather than read-only",
    batch: "R5",
  },
  {
    field: "expansion_map",
    why: "spec 18 requires it to render; the learner needs a next step",
    batch: "R6",
  },
];

/** A field the user must be able to correct without editing JSON. */
const MUST_BE_EDITABLE: { kind: keyof typeof DRAFT_EDITABLE_FIELDS; field: string; why: string }[] = [
  {
    kind: "stages",
    field: "example",
    why: "the R1 gate blocks publication without one, so the user must be able to add one",
  },
  {
    kind: "stages",
    field: "implementation_details",
    why: "the other half of the R1 gate; a blocked publish with no way to fix it is a dead end",
  },
  {
    kind: "operations",
    field: "common_failures",
    why: "the R1/R4 gate reports it, so the user must be able to supply it",
  },
];

describe("artifact field coverage", () => {
  it("finds the surfaces it is meant to inspect", () => {
    // If this drops to zero the checks below pass vacuously, which is the one
    // failure mode a source-scanning test has.
    expect(SURFACES.length).toBeGreaterThan(15);
    expect(surfacesMentioning("local_goal").length).toBeGreaterThan(0);
  });

  describe.each(MUST_BE_READABLE.map((r) => [r.field, r] as const))(
    "%s",
    (_field, requirement) => {
      it("is rendered somewhere the user can reach", () => {
        const found = surfacesMentioning(requirement.field);
        expect(
          found.length,
          `'${requirement.field}' has no user entry point, and ${requirement.why}. ` +
            `Batch ${requirement.batch} must render it. ` +
            `Searched ${SURFACES.length} files under app/ and components/.`,
        ).toBeGreaterThan(0);
      });
    },
  );

  describe.each(MUST_BE_EDITABLE.map((r) => [`${r.kind}.${r.field}`, r] as const))(
    "%s",
    (_label, requirement) => {
      it("is editable in a draft", () => {
        const fields: readonly string[] = DRAFT_EDITABLE_FIELDS[requirement.kind];
        expect(
          fields,
          `'${requirement.kind}.${requirement.field}' cannot be corrected by the user, and ` +
            `${requirement.why}. Currently editable: ${fields.join(", ") || "(nothing)"}`,
        ).toContain(requirement.field);
      });
    },
  );

  it("keeps structural reference fields read-only in drafts", () => {
    // The opposite direction, and the one that must never regress: a form that
    // could edit `stage_refs` would let a client drop a Stage from the main
    // line, which is the failure this product exists to prevent.
    const editable = Object.values(DRAFT_EDITABLE_FIELDS).flat();
    const forbidden = editable.filter((field) => field.endsWith("_ref") || field.endsWith("_refs"));

    expect(forbidden).toEqual([]);
  });

  it("does not offer an editable field the schema does not define", () => {
    // A field editable in the UI but absent from the canonical schema would be
    // accepted by the form and then dropped on save, losing the user's work.
    // Collections are `{"type": "array", "items": {"properties": {...}}}` in the
    // canonical schema, so the field map lives one level deeper than it looks.
    const schema = JSON.parse(
      readFileSync(join(WEB_ROOT, "..", "..", "schemas", "cop-artifact.schema.json"), "utf8"),
    ) as {
      properties: Record<string, { items?: { properties?: Record<string, unknown> } }>;
    };
    const collection = {
      goals: "goals",
      processes: "main_processes",
      stages: "stages",
      concepts: "concepts",
      operations: "operations",
    } as const;

    const unknown: string[] = [];
    for (const [kind, name] of Object.entries(collection)) {
      const defined = Object.keys(schema.properties[name]?.items?.properties ?? {});
      for (const field of DRAFT_EDITABLE_FIELDS[kind as keyof typeof collection]) {
        if (!defined.includes(field)) unknown.push(`${kind}.${field}`);
      }
    }

    expect(unknown).toEqual([]);
  });
});
