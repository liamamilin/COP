import Markdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { githubFile, safeHttp } from "./lib";

interface Tree {
  type: string;
  value?: string;
  children?: Tree[];
  data?: Record<string, unknown>;
}
// Preserve ONLY exact named anchors used by the research reports. All other raw
// HTML stays untrusted and is discarded by react-markdown's skipHtml.
function reportAnchors() {
  return (tree: Tree) => {
    let heading = 0;
    function visit(node: Tree) {
      if (node.type === "heading")
        node.data = { hProperties: { id: `report-h-${heading++}` } };
      if (node.type === "html") {
        const match = /^<a\s+id=["']([a-zA-Z0-9_-]+)["']\s*>(?:<\/a>)?$/.exec(
          node.value?.trim() || "",
        );
        if (match) {
          node.type = "text";
          node.value = "";
          node.children = undefined;
          node.data = {
            hName: "span",
            hProperties: { id: "report-" + match[1] },
          };
        }
      }
      node.children?.forEach(visit);
    }
    visit(tree);
  };
}
export function reportHeadings(markdown: string) {
  let fenced = false;
  let index = 0;
  return markdown.split("\n").flatMap((line) => {
    if (/^\s*(```|~~~)/.test(line)) {
      fenced = !fenced;
      return [];
    }
    const m = !fenced && /^(#{1,6})\s+(.+)$/.exec(line);
    if (!m) return [];
    const item = {
      id: `report-h-${index++}`,
      text: m[2].replace(/[*`]/g, ""),
      level: m[1].length,
    };
    return item.level <= 2 ? [item] : [];
  });
}
export function scrollReport(id: string) {
  const target = document.getElementById(id);
  target?.scrollIntoView({ block: "start" });
}
export function SafeMarkdown({
  children,
  slug,
  revision,
}: {
  children: string;
  slug: string;
  revision: string;
}) {
  function url(value: string) {
    if (/^#[a-zA-Z0-9_-]+$/.test(value)) return "#report-" + value.slice(1);
    if (
      [
        "possibilities.json",
        "possibilities.md",
        "validation-report.txt",
        "discovery-log.md",
        "source-coverage.json",
      ].includes(value)
    )
      return githubFile(slug, value, revision);
    return safeHttp(value);
  }
  return (
    <Markdown
      skipHtml
      remarkPlugins={[remarkGfm, reportAnchors]}
      urlTransform={url}
      components={{
        a: ({ href, children }) =>
          !href ? (
            <span>{children}</span>
          ) : href.startsWith("#report-") ? (
            <a
              href={href}
              onClick={(e) => {
                e.preventDefault();
                scrollReport(href.slice(1));
              }}
            >
              {children}
            </a>
          ) : (
            <a href={href} target="_blank" rel="noopener noreferrer">
              {children}
              <span className="sr-only">（新窗口）</span>
            </a>
          ),
        img: ({ alt }) => <span>{alt ? `[图片：${alt}]` : ""}</span>,
        h1: ({ children, ...props }) => <h2 {...props}>{children}</h2>,
        table: ({ children }) => (
          <div className="table-scroll">
            <table>{children}</table>
          </div>
        ),
      }}
    >
      {children}
    </Markdown>
  );
}
