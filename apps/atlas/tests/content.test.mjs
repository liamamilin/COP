import { describe, it, expect } from "vitest";
import {
  collectContent,
  validateCatalog,
  validateMap,
  root,
} from "../scripts/content.mjs";
import { readFile, mkdtemp, mkdir, writeFile, rm, symlink } from "node:fs/promises";
import { tmpdir } from "node:os";
import { join } from "node:path";

const fixture = JSON.parse(
  await readFile(
    join(root, "outputs/langchain-agent/possibilities.json"),
    "utf8",
  ),
);
describe("build content contract", () => {
  it("loads the complete v0.2 handoff through the real collector while preserving the active catalog", async () => {
    const activePath = join(root, "catalog/p-atlas-topics.v0.1.json");
    const activeBefore = await readFile(activePath, "utf8");
    const candidate = JSON.parse(
      await readFile(join(root, "catalog/p-atlas-topics.v0.2.json"), "utf8"),
    );
    const dir = await mkdtemp(join(tmpdir(), "atlas-v02-contract-"));
    try {
      await mkdir(join(dir, "catalog"));
      await writeFile(
        join(dir, "catalog/p-atlas-topics.v0.1.json"),
        JSON.stringify(candidate),
      );
      await symlink(join(root, "outputs"), join(dir, "outputs"), "dir");
      const { library, bundles } = await collectContent(dir, false);
      expect(bundles).toHaveLength(38);
      expect(library.search).toHaveLength(726);
      expect(bundles.map((b) => b.slug)).toEqual(
        candidate.topics.filter((t) => t.status === "ready").map((t) => t.slug),
      );
      for (const b of bundles) {
        const expected = JSON.parse(
          await readFile(join(root, "outputs", b.slug, "possibilities.json"), "utf8"),
        );
        expect(b.map).toEqual(expected);
        expect(b.markdown).toContain(b.map.coverage_gaps[0]);
      }
    } finally {
      await rm(dir, { recursive: true, force: true });
    }
    expect(await readFile(activePath, "utf8")).toBe(activeBefore);
  });
  it("reads every real P and report from outputs, preserving original fields", async () => {
    const { library, bundles } = await collectContent(root, false);
    const catalog = JSON.parse(
      await readFile(join(root, "catalog/p-atlas-topics.v0.1.json"), "utf8"),
    );
    expect(library.catalog).toEqual(catalog);
    expect(bundles.map((b) => b.slug)).toEqual(
      catalog.topics.filter((t) => t.status === "ready").map((t) => t.slug),
    );
    expect(library.summaries.map((s) => [s.slug, s.count])).toEqual(
      bundles.map((b) => [b.slug, b.map.possibilities.length]),
    );
    expect(library.search).toEqual(
      bundles.flatMap((b) =>
        b.map.possibilities.map((possibility) => ({ slug: b.slug, possibility })),
      ),
    );
    for (const [slug, count] of [["ggplot2", 74], ["langchain-agent", 53], ["obsidian", 63]])
      expect(library.summaries.find((s) => s.slug === slug)?.count).toBe(count);
    expect(
      library.catalog.topics.filter((t) => t.status === "planned"),
    ).toEqual(catalog.topics.filter((t) => t.status === "planned"));
    for (const b of bundles) {
      expect(b.map).toEqual(
        JSON.parse(
          await readFile(
            join(root, "outputs", b.slug, "possibilities.json"),
            "utf8",
          ),
        ),
      );
      expect(b.markdown).toEqual(
        await readFile(
          join(root, "outputs", b.slug, "possibilities.md"),
          "utf8",
        ),
      );
    }
    for (const summary of library.summaries)
      expect(summary.researchDate).toMatch(/^\d{4}-\d{2}-\d{2}$/);
  });
  it("rejects broken IDs, references, URLs, fabricated quotes, and unsupported review labels", () => {
    const bads = [
      (d) => (d.sources[0].url = "javascript:alert(1)"),
      (d) => d.possibilities[0].source_ids.push("unknown-source"),
      (d) => d.possibilities[0].group_ids.push("unknown-group"),
      (d) => (d.groups[0].id = d.sources[0].id),
      (d) => (d.possibilities[0].evidence_refs[0].quote = "invented passage"),
      (d) => (d.possibilities[0].status = "reviewed"),
      (d) => {
        d.possibilities[0].availability = "extension";
        d.possibilities[0].conditions = "";
      },
    ];
    for (const change of bads) {
      const d = structuredClone(fixture);
      change(d);
      expect(() => validateMap(d)).toThrow();
    }
  });
  it("keeps proposed entries unconfirmed and supports optional metadata", () => {
    const d = structuredClone(fixture);
    const p = d.possibilities.find((p) => p.status === "proposed");
    p.source_ids = [];
    p.evidence_refs = [];
    delete d.possibilities[0].required_components;
    expect(() => validateMap(d)).not.toThrow();
  });
  it("rejects malformed JSON / missing ready assets, but never requires planned assets", async () => {
    const dir = await mkdtemp(join(tmpdir(), "atlas-contract-"));
    try {
      await mkdir(join(dir, "catalog"));
      const c = {
        schema_version: "0.1",
        domains: [{ id: "d", title: "domain" }],
        topics: [
          {
            slug: "not-generated",
            title: "Plan",
            description: "Research plan",
            domain_id: "d",
            status: "planned",
          },
        ],
      };
      await writeFile(
        join(dir, "catalog/p-atlas-topics.v0.1.json"),
        JSON.stringify(c),
      );
      expect((await collectContent(dir, false)).bundles).toHaveLength(0);
      c.topics[0].status = "ready";
      await writeFile(
        join(dir, "catalog/p-atlas-topics.v0.1.json"),
        JSON.stringify(c),
      );
      await expect(collectContent(dir, false)).rejects.toThrow();
      await mkdir(join(dir, "outputs/not-generated"), { recursive: true });
      await Promise.all(
        ["possibilities.json", "possibilities.md", "validation-report.txt"].map(
          (f) =>
            writeFile(
              join(dir, "outputs/not-generated", f),
              f === "possibilities.json" ? "{broken" : "body",
            ),
        ),
      );
      await expect(collectContent(dir, false)).rejects.toThrow();
    } finally {
      await rm(dir, { recursive: true, force: true });
    }
  });
  it("rejects traversal slugs and unknown domains before reading files", () => {
    const c = {
      schema_version: "0.1",
      domains: [{ id: "d", title: "D" }],
      topics: [
        {
          slug: "../bad",
          title: "T",
          description: "D",
          domain_id: "d",
          status: "ready",
        },
      ],
    };
    expect(() => validateCatalog(c)).toThrow();
    c.topics[0].slug = "good";
    c.topics[0].domain_id = "missing";
    expect(() => validateCatalog(c)).toThrow();
  });
});
