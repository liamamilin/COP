import { readFile, mkdir, writeFile, rm } from "node:fs/promises";
import { resolve, dirname } from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";
import { createHash } from "node:crypto";
import { execFileSync } from "node:child_process";

export const root = resolve(
  dirname(fileURLToPath(import.meta.url)),
  "../../..",
);
const text = (x) => typeof x === "string" && x.trim().length > 0;
function assert(ok, message) {
  if (!ok) throw new Error(message);
}
function strings(value) {
  return Array.isArray(value) && value.every(text);
}
function unique(items, label) {
  const ids = items.map((x) => x.id);
  assert(
    ids.every(text) && new Set(ids).size === ids.length,
    `${label}: duplicate or missing IDs`,
  );
}
export function validateCatalog(c) {
  assert(
    c?.schema_version === "0.1" &&
      Array.isArray(c.domains) &&
      Array.isArray(c.topics),
    "Invalid catalog",
  );
  unique(c.domains, "domains");
  const ids = new Set(c.domains.map((d) => d.id));
  const slugs = new Set();
  for (const d of c.domains) assert(text(d.title), "Domain title required");
  for (const t of c.topics) {
    assert(
      /^[a-z0-9]+(?:-[a-z0-9]+)*$/.test(t.slug) && !slugs.has(t.slug),
      "Invalid or duplicate topic slug",
    );
    slugs.add(t.slug);
    assert(
      text(t.title) &&
        text(t.description) &&
        ids.has(t.domain_id) &&
        ["ready", "planned"].includes(t.status),
      `Invalid catalog topic ${t.slug}`,
    );
  }
}
export function validateMap(d) {
  assert(
    d?.schema_version === "0.1" && text(d.topic?.name) && text(d.topic?.scope),
    "Invalid map topic",
  );
  for (const key of ["sources", "groups", "possibilities", "coverage_gaps"])
    assert(Array.isArray(d[key]), `Missing ${key}`);
  const all = [...d.sources, ...d.groups, ...d.possibilities];
  unique(all, "map");
  const sources = new Map(d.sources.map((s) => [s.id, s]));
  const groups = new Set(d.groups.map((g) => g.id));
  for (const s of d.sources)
    assert(
      text(s.title) && /^https?:\/\//i.test(s.url) && text(s.evidence),
      `Invalid source ${s.id}`,
    );
  for (const g of d.groups) assert(text(g.name), `Invalid group ${g.id}`);
  for (const p of d.possibilities) {
    assert(
      text(p.title) &&
        text(p.result) &&
        ["core", "extension", "unknown"].includes(p.availability) &&
        ["source_supported", "proposed", "reviewed"].includes(p.status),
      `Invalid possibility ${p.id}`,
    );
    assert(
      strings(p.source_ids) && strings(p.group_ids),
      `Invalid references ${p.id}`,
    );
    for (const [refs, registry] of [
      [p.source_ids, sources],
      [p.group_ids, groups],
    ])
      assert(
        new Set(refs).size === refs.length &&
          refs.every((id) => registry.has(id)),
        `Unknown/duplicate reference ${p.id}`,
      );
    if (p.availability === "extension")
      assert(text(p.conditions), `Extension conditions required ${p.id}`);
    if (p.status === "reviewed")
      assert(
        text(p.reviewed_by) ||
          (p.reviewed_by &&
            typeof p.reviewed_by === "object" &&
            !Array.isArray(p.reviewed_by) &&
            Object.keys(p.reviewed_by).length),
        `Missing human review record ${p.id}`,
      );
    if (p.status !== "proposed")
      assert(p.evidence_refs?.length > 0, `Missing evidence ${p.id}`);
    for (const e of p.evidence_refs || [])
      assert(
        p.source_ids.includes(e.source_id) &&
          text(e.quote) &&
          sources.get(e.source_id)?.evidence.includes(e.quote),
        `Invalid quote ${p.id}`,
      );
  }
  assert(
    d.coverage_gaps.every((g) => typeof g === "string"),
    "Invalid coverage gaps",
  );
}
export function researchDate(d) {
  return (
    d.research_method?.collection_date_local ||
    d.sources
      .map((s) => s.retrieved_on || s.retrieved_date)
      .filter(Boolean)
      .sort()
      .at(-1) ||
    d.generated_at?.slice(0, 10) ||
    "未注明"
  );
}
export async function collectContent(repoRoot, validateWithSkill = true) {
  const catalog = JSON.parse(
    await readFile(
      resolve(repoRoot, "catalog/p-atlas-topics.v0.1.json"),
      "utf8",
    ),
  );
  validateCatalog(catalog);
  const bundles = [];
  const summaries = [];
  const search = [];
  let revision;
  try {
    revision = execFileSync("git", ["rev-parse", "HEAD"], {
      cwd: repoRoot,
      encoding: "utf8",
      stdio: ["ignore", "pipe", "ignore"],
    }).trim();
  } catch {
    revision = "proposal/cop-capability-map-v0";
  }
  for (const topic of catalog.topics.filter((t) => t.status === "ready")) {
    const dir = resolve(repoRoot, "outputs", topic.slug);
    const [json, markdown, validationReport] = await Promise.all(
      ["possibilities.json", "possibilities.md", "validation-report.txt"].map(
        (f) => readFile(resolve(dir, f), "utf8"),
      ),
    );
    assert(
      markdown.trim() && validationReport.trim(),
      `Empty report ${topic.slug}`,
    );
    const map = JSON.parse(json);
    validateMap(map);
    if (validateWithSkill)
      execFileSync(
        "python3",
        [
          "-B",
          resolve(repoRoot, ".agents/skills/p-discovery/scripts/validate.py"),
          resolve(dir, "possibilities.json"),
        ],
        { stdio: "inherit" },
      );
    const summary = {
      slug: topic.slug,
      count: map.possibilities.length,
      groups: map.groups.length,
      supported: map.possibilities.filter((p) => p.status !== "proposed")
        .length,
      proposed: map.possibilities.filter((p) => p.status === "proposed").length,
      researchDate: researchDate(map),
      scope: map.topic.scope,
    };
    summaries.push(summary);
    search.push(
      ...map.possibilities.map((p) => ({ slug: topic.slug, possibility: p })),
    );
    bundles.push({
      slug: topic.slug,
      map,
      markdown,
      validationReport,
      provenance: {
        revision,
        jsonSha256: createHash("sha256").update(json).digest("hex"),
        markdownSha256: createHash("sha256").update(markdown).digest("hex"),
      },
    });
  }
  return { library: { catalog, summaries, search, revision }, bundles };
}
export async function generate() {
  const { library, bundles } = await collectContent(root);
  const app = resolve(root, "apps/atlas");
  await mkdir(resolve(app, "src/generated"), { recursive: true });
  await rm(resolve(app, "public/content"), { recursive: true, force: true });
  await mkdir(resolve(app, "public/content"), { recursive: true });
  await writeFile(
    resolve(app, "src/generated/library.json"),
    JSON.stringify(library),
  );
  for (const b of bundles)
    await writeFile(
      resolve(app, `public/content/${b.slug}.json`),
      JSON.stringify(b),
    );
  console.log(
    `Atlas: ${bundles.length} ready topics; ${library.search.length} P; ${library.catalog.topics.filter((t) => t.status === "planned").length} planned. Content read from outputs/.`,
  );
}
if (
  process.argv[1] &&
  import.meta.url === pathToFileURL(resolve(process.argv[1])).href
)
  await generate();
