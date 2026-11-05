import { describe, it, expect } from "vitest";
import { renderToStaticMarkup } from "react-dom/server";
import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import type { AtlasMap, Possibility } from "../src/types";
import {
  blankRoute,
  filterPs,
  goalText,
  matches,
  parseRoute,
  routeHash,
  safeHttp,
  statusLabel,
} from "../src/lib";
import { SafeMarkdown, reportHeadings } from "../src/Report";

const map = JSON.parse(
  readFileSync(
    resolve("../../outputs/langchain-agent/possibilities.json"),
    "utf8",
  ),
) as AtlasMap;
describe("reading behavior", () => {
  it("round trips shareable paths, filters, Unicode queries and source/report views", () => {
    for (const extra of [
      {
        slug: "obsidian",
        pid: "p-knowledge-network",
        q: "知识 库",
        group: "g-connect",
        availability: "core",
        status: "supported",
      },
      { slug: "obsidian", view: "report" as const },
      { slug: "obsidian", view: "sources" as const, sourceId: "s-pdf" },
    ]) {
      const r = { ...blankRoute, ...extra };
      expect(parseRoute(routeHash(r))).toEqual(r);
    }
    expect(parseRoute("#/topic/%E0%A4%A").invalid).toBe(true);
    expect(parseRoute("#/bad/path").invalid).toBe(true);
  });
  it("searches titles, outcomes, aliases, components and keywords case insensitively", () => {
    const p = {
      ...map.possibilities[0],
      keywords: ["SPECIAL"],
      aliases: ["工具型助手"],
    };
    expect(matches(p, "工具型助手")).toBe(true);
    expect(matches(p, "special")).toBe(true);
    expect(matches(p, "LangChain Python")).toBe(true);
    expect(matches(p, "not-a-result")).toBe(false);
  });
  it("filters combined criteria and keeps multi-group results unique", () => {
    const p = { ...map.possibilities[0], group_ids: ["a", "b"] };
    const r = {
      ...blankRoute,
      group: "b",
      availability: "core",
      status: "supported",
    };
    expect(filterPs([p], r)).toEqual([p]);
    expect(filterPs([p], { ...r, q: "impossible-query" })).toEqual([]);
    expect(
      filterPs(map.possibilities, { ...blankRoute, status: "proposed" }).map(
        (p) => p.id,
      ),
    ).toEqual(["p-generative-ui"]);
  });
  it("never labels proposed or unreviewed entries as human reviewed", () => {
    expect(statusLabel(map.possibilities[0])).toBe("来源支持，未必实测");
    expect(
      statusLabel({
        ...map.possibilities[0],
        status: "reviewed",
        reviewed_by: undefined,
      }),
    ).not.toContain("人工复核");
  });
  it("copies the exact result and conditions with topic, dependencies, status and source URLs", () => {
    const p = map.possibilities.find(
      (p) => p.status === "proposed",
    ) as Possibility;
    const text = goalText(map.topic.name, p, map.sources);
    expect(text).toContain(p.result);
    expect(text).toContain(p.conditions);
    expect(text).toContain("待验证方向");
    expect(text).toContain(
      map.sources.find((s) => s.id === p.source_ids[0])!.url,
    );
  });
  it("copies precise evidence links and falls back when a locator URL is unsafe", () => {
    const base = map.possibilities[0];
    const source = map.sources.find((s) => s.id === base.source_ids[0])!;
    const url = "https://github.com/example/repo/blob/abc/docs/usage.md#L10-L14";
    const p = {
      ...base,
      evidence_refs: [{ source_id: source.id, quote: source.evidence, url }],
    };
    expect(goalText(map.topic.name, p, map.sources)).toContain(url);
    const unsafe = { ...p, evidence_refs: [{ ...p.evidence_refs[0], url: "javascript:alert(1)" }] };
    expect(goalText(map.topic.name, unsafe, map.sources)).toContain(source.url);
    expect(goalText(map.topic.name, unsafe, map.sources)).not.toContain("javascript:");
  });
  it("renders Markdown without executable HTML, unsafe links or external image requests", () => {
    const html = renderToStaticMarkup(
      <SafeMarkdown slug="obsidian" revision="test">
        {
          '<script>alert(1)</script>\n\n<img src=x onerror=alert(2)>\n\n[bad](javascript:alert%281%29)\n\n[good](https://example.com)\n\n![external](https://evil.test/track.png)\n\n<a id="g-test"></a>\n\n## Heading\n\n[local](#g-test)\n\n[JSON](possibilities.json)\n\n[Discovery](discovery-log.md)\n\n[Coverage](source-coverage.json)\n\n[Unknown](untrusted.html)'
        }
      </SafeMarkdown>,
    );
    expect(html).not.toMatch(/<script|<img|onerror=|href="javascript:/);
    expect(html).toContain('id="report-g-test"');
    expect(html).toContain('target="_blank" rel="noopener noreferrer"');
    expect(html).toContain(
      "github.com/liamamilin/COP/blob/test/outputs/obsidian/possibilities.json",
    );
    for (const file of ["discovery-log.md", "source-coverage.json"])
      expect(html).toContain(
        `github.com/liamamilin/COP/blob/test/outputs/obsidian/${file}`,
      );
    expect(html).not.toContain('href="untrusted.html"');
    expect(safeHttp("data:text/html,bad")).toBeUndefined();
    expect(safeHttp("//evil.test")).toBeUndefined();
  });
  it("builds a report table of contents, ignoring code fences", () => {
    expect(
      reportHeadings(
        "# Title\n\n## First\n```md\n## Not a heading\n```\n### Small\n## Last",
      ).map((h) => h.text),
    ).toEqual(["Title", "First", "Last"]);
  });
});
