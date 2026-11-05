import type { AtlasMap, Possibility, Route, Source } from "./types";

export const blankRoute: Route = {
  view: "map",
  q: "",
  group: "",
  availability: "",
  status: "",
  domain: "",
};
export function parseRoute(hash: string): Route {
  try {
    const [path, query] = hash.replace(/^#/, "").split("?");
    const qs = new URLSearchParams(query);
    const parts = (path || "/")
      .split("/")
      .filter(Boolean)
      .map(decodeURIComponent);
    const r = {
      ...blankRoute,
      q: qs.get("q") || "",
      group: qs.get("group") || "",
      availability: qs.get("availability") || "",
      status: qs.get("status") || "",
      domain: qs.get("domain") || "",
    };
    if (!parts.length) return r;
    if (parts[0] !== "topic" || !parts[1]) return { ...r, invalid: true };
    const result: Route = { ...r, slug: parts[1] };
    if (parts.length === 2) return result;
    if (parts[2] === "report" && parts.length === 3)
      return { ...result, view: "report" };
    if (parts[2] === "sources" && parts.length <= 4)
      return { ...result, view: "sources", sourceId: parts[3] };
    if (parts[2] === "p" && parts.length === 4)
      return { ...result, pid: parts[3] };
    return { ...r, invalid: true };
  } catch {
    return { ...blankRoute, invalid: true };
  }
}
export function routeHash(r: Partial<Route> = {}): string {
  let path = r.slug ? "/topic/" + encodeURIComponent(r.slug) : "/";
  if (r.slug && r.view === "report") path += "/report";
  else if (r.slug && r.view === "sources")
    path +=
      "/sources" + (r.sourceId ? "/" + encodeURIComponent(r.sourceId) : "");
  else if (r.slug && r.pid) path += "/p/" + encodeURIComponent(r.pid);
  const q = new URLSearchParams();
  for (const k of ["q", "group", "availability", "status", "domain"] as const)
    if (r[k]) q.set(k, r[k]!);
  return "#" + path + (q.size ? "?" + q : "");
}
export function navigate(r: Partial<Route>, replace = false) {
  const hash = routeHash(r);
  if (replace) {
    history.replaceState(null, "", hash);
    window.dispatchEvent(new Event("hashchange"));
  } else if (window.location.hash !== hash) window.location.hash = hash;
}
export function matches(p: Possibility, query: string) {
  const text = [
    p.title,
    p.result,
    p.conditions,
    ...(p.aliases || []),
    ...(p.keywords || []),
    ...(p.required_components || []),
  ]
    .join(" ")
    .normalize("NFKC")
    .toLocaleLowerCase();
  return query
    .normalize("NFKC")
    .trim()
    .toLocaleLowerCase()
    .split(/\s+/)
    .filter(Boolean)
    .every((term) => text.includes(term));
}
export function filterPs(
  ps: Possibility[],
  r: Pick<Route, "q" | "group" | "availability" | "status">,
) {
  return ps.filter(
    (p) =>
      matches(p, r.q) &&
      (!r.group || p.group_ids.includes(r.group)) &&
      (!r.availability || p.availability === r.availability) &&
      (!r.status ||
        (r.status === "supported"
          ? p.status !== "proposed"
          : p.status === r.status)),
  );
}
export const availabilityLabel = (p: Possibility) =>
  ({ core: "核心 / 内置", extension: "扩展", unknown: "路径待核实" })[
    p.availability
  ];
export function statusLabel(p: Possibility) {
  if (p.status === "proposed") return "待验证方向";
  if (p.status === "reviewed" && p.reviewed_by) return "人工复核 · 见记录";
  return "来源支持，未必实测";
}
export function safeHttp(url: unknown): string | undefined {
  if (typeof url !== "string") return;
  try {
    const u = new URL(url);
    return ["http:", "https:"].includes(u.protocol) ? u.href : undefined;
  } catch {
    return;
  }
}
export function githubFile(slug: string, file: string, revision: string) {
  return `https://github.com/liamamilin/COP/blob/${encodeURIComponent(revision)}/outputs/${encodeURIComponent(slug)}/${encodeURIComponent(file)}`;
}
export function goalText(topic: string, p: Possibility, sources: Source[]) {
  return [
    `主题：${topic}`,
    `目标：${p.title}`,
    `可观察结果：${p.result}`,
    `条件与边界：${p.conditions || "原研究未注明，请先核对。"}`,
    `能力路径：${availabilityLabel(p)}${p.capability_layer ? "；" + p.capability_layer : ""}`,
    ...(p.required_components?.length
      ? ["必要组件：" + p.required_components.join("；")]
      : []),
    `证据状态：${statusLabel(p)}。来源支持不等于已运行实测。`,
    "来源：",
    ...sources
      .filter((s) => p.source_ids.includes(s.id) && safeHttp(s.url))
      .flatMap((s) => {
        const located = [...new Set(
          (p.evidence_refs || [])
            .filter((e) => e.source_id === s.id)
            .map((e) => safeHttp(e.url))
            .filter((url): url is string => !!url),
        )];
        return (located.length ? located : [s.url]).map((url) => `${s.title}\n${url}`);
      }),
  ].join("\n\n");
}
export function sourceUsage(map: AtlasMap, id: string) {
  return map.possibilities.filter((p) => p.source_ids.includes(id));
}
