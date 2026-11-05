import { useEffect, useRef, useState, type ReactNode } from "react";
import libraryData from "./generated/library.json";
import type {
  AtlasMap,
  Bundle,
  Library,
  Possibility,
  Route,
  Source,
  Topic,
} from "./types";
import {
  availabilityLabel,
  blankRoute,
  filterPs,
  githubFile,
  goalText,
  matches,
  navigate,
  parseRoute,
  routeHash,
  safeHttp,
  sourceUsage,
  statusLabel,
} from "./lib";
import { reportHeadings, SafeMarkdown, scrollReport } from "./Report";

const library = libraryData as unknown as Library;
const cache = new Map<string, Bundle>();
const summary = (slug: string) =>
  library.summaries.find((s) => s.slug === slug)!;
const domainName = (id: string) =>
  library.catalog.domains.find((d) => d.id === id)?.title || id;
const layerNames: Record<string, string> = {
  built_in: "Obsidian 内置",
  community_plugin: "社区插件",
  official_plugin: "官方另装插件",
  official_browser_extension: "官方浏览器扩展",
  third_party_service: "第三方服务 / 模型路线",
  third_party_tool: "第三方工具",
  official_paid_service: "官方付费服务",
  multiple_routes: "多种实现路线",
  langchain_api: "LangChain 公开接口",
  langgraph_runtime_interface: "LangGraph 运行与存储入口",
  unverified_python_frontend_integration: "Python 前端接入待验证",
};
function External({ url, children }: { url: unknown; children: ReactNode }) {
  const href = safeHttp(url);
  return href ? (
    <a href={href} target="_blank" rel="noopener noreferrer">
      {children}
      <span aria-hidden="true"> ↗</span>
      <span className="sr-only">（新窗口）</span>
    </a>
  ) : (
    <span>{children}</span>
  );
}
function Status({ p }: { p: Possibility }) {
  return (
    <span className={"status " + (p.status === "proposed" ? "tentative" : "")}>
      {statusLabel(p)}
    </span>
  );
}
function Empty({ title, children }: { title: string; children?: ReactNode }) {
  return (
    <div className="empty">
      <span aria-hidden="true">⌕</span>
      <h2>{title}</h2>
      {children}
    </div>
  );
}
function RawLinks({ slug, revision }: { slug: string; revision: string }) {
  return (
    <div className="raw-links">
      <External url={githubFile(slug, "possibilities.md", revision)}>
        原始 Markdown
      </External>
      <External url={githubFile(slug, "possibilities.json", revision)}>
        原始 JSON
      </External>
      <External url={githubFile(slug, "validation-report.txt", revision)}>
        研究校验记录
      </External>
    </div>
  );
}
function Filters({
  route,
  update,
}: {
  route: Route;
  update: (r: Partial<Route>) => void;
}) {
  return (
    <div className="filters">
      <label>
        <span className="sr-only">能力路径</span>
        <select
          aria-label="能力路径"
          value={route.availability}
          onChange={(e) => update({ availability: e.target.value })}
        >
          <option value="">全部能力路径</option>
          <option value="core">核心 / 内置</option>
          <option value="extension">扩展</option>
          <option value="unknown">路径待核实</option>
        </select>
      </label>
      <label>
        <span className="sr-only">证据状态</span>
        <select
          aria-label="证据状态"
          value={route.status}
          onChange={(e) => update({ status: e.target.value })}
        >
          <option value="">全部证据状态</option>
          <option value="supported">有来源支持</option>
          <option value="proposed">待验证方向</option>
          <option value="reviewed">人工复核</option>
        </select>
      </label>
      {(route.q || route.group || route.availability || route.status) && (
        <button
          className="text-button"
          onClick={() =>
            update({ q: "", group: "", availability: "", status: "" })
          }
        >
          重置筛选
        </button>
      )}
    </div>
  );
}
function PLink({
  p,
  slug,
  active = false,
  query = "",
  route,
}: {
  p: Possibility;
  slug: string;
  active?: boolean;
  query?: string;
  route?: Route;
}) {
  return (
    <a
      className={
        "p-card " +
        (active ? "active " : "") +
        (p.status === "proposed" ? "is-proposed" : "")
      }
      href={routeHash({ ...route, slug, pid: p.id, q: query })}
      aria-current={active ? "true" : undefined}
    >
      <div className="card-meta">
        <span>{availabilityLabel(p)}</span>
        <span className="p-id">{p.id}</span>
      </div>
      <h3>
        {p.title}
        <span aria-hidden="true"> ↗</span>
      </h3>
      <p>{p.result}</p>
      <Status p={p} />
    </a>
  );
}
function LibraryPage({ route }: { route: Route }) {
  const topics = library.catalog.topics.filter(
    (t) => !route.domain || t.domain_id === route.domain,
  );
  const topicMatch = (t: Topic) =>
    [t.title, t.description, domainName(t.domain_id)]
      .join(" ")
      .toLocaleLowerCase()
      .includes(route.q.trim().toLocaleLowerCase());
  const ready = topics.filter((t) => t.status === "ready" && topicMatch(t));
  const planned = topics.filter((t) => t.status === "planned" && topicMatch(t));
  const hits = route.q.trim()
    ? library.search.filter(
        ({ slug, possibility }) =>
          topics.some((t) => t.slug === slug) &&
          matches(possibility, route.q) &&
          filterPs([possibility], { ...route, group: "" }).length,
      )
    : [];
  const [limit, setLimit] = useState(30);
  useEffect(
    () => setLimit(30),
    [route.q, route.domain, route.availability, route.status],
  );
  return (
    <div className="library-shell">
      <section className="hero">
        <div>
          <p className="eyebrow">POSSIBILITY ATLAS / v0.1</p>
          <h1>
            探索一个主题
            <br />
            可以做成什么<span className="period">。</span>
          </h1>
          <p className="hero-description">
            从可实现的结果出发，了解条件，追溯来源。
            <br />
            找到值得继续探索的下一件事。
          </p>
        </div>
        <div className="hero-note">
          <span className="line-icon" aria-hidden="true">
            P
          </span>
          <p>
            让可能性
            <br />
            有据可循。
          </p>
          <span>研究地图 · 条件边界 · 原始来源</span>
        </div>
      </section>
      <form
        className="library-search"
        onSubmit={(e) => e.preventDefault()}
        role="search"
        aria-label="图书馆内容搜索"
      >
        <span aria-hidden="true">⌕</span>
        <input
          aria-label="搜索主题与可能性"
          placeholder="搜索主题、你想完成的事，或一个关键词…"
          value={route.q}
          onChange={(e) => navigate({ ...route, q: e.target.value }, true)}
        />
        {route.q && (
          <button
            type="button"
            aria-label="清除搜索"
            onClick={() => navigate({ ...route, q: "" }, true)}
          >
            ×
          </button>
        )}
        <span className="search-caption">站内搜索</span>
      </form>
      <nav className="domain-nav" aria-label="领域导航">
        <button
          aria-pressed={!route.domain}
          onClick={() => navigate({ ...route, domain: "" }, true)}
        >
          全部领域
        </button>
        {library.catalog.domains.map((d) => (
          <button
            key={d.id}
            aria-pressed={route.domain === d.id}
            onClick={() => navigate({ ...route, domain: d.id }, true)}
          >
            {d.title}
          </button>
        ))}
      </nav>
      {route.q.trim() && (
        <section className="global-results" aria-labelledby="search-title">
          <div className="section-heading">
            <div>
              <p className="eyebrow">SEARCH THE ATLAS</p>
              <h2 id="search-title">可能性搜索</h2>
            </div>
            <span role="status">{hits.length} 项匹配结果</span>
          </div>
          <Filters
            route={route}
            update={(patch) => navigate({ ...route, ...patch }, true)}
          />
          {hits.length ? (
            <>
              <div className="search-grid">
                {hits.slice(0, limit).map(({ slug, possibility: p }) => (
                  <div key={slug + "/" + p.id}>
                    <p className="search-topic">
                      {
                        library.catalog.topics.find((t) => t.slug === slug)
                          ?.title
                      }
                    </p>
                    <PLink p={p} slug={slug} query={route.q} />
                  </div>
                ))}
              </div>
              {hits.length > limit && (
                <button
                  className="secondary-button load-more"
                  onClick={() => setLimit((v) => v + 30)}
                >
                  再显示 30 项
                </button>
              )}
            </>
          ) : (
            <Empty title="没有找到匹配的可能性">
              <p>试试更短的关键词，或重置筛选。</p>
            </Empty>
          )}
        </section>
      )}
      <section aria-labelledby="ready-title">
        <div className="section-heading">
          <div>
            <p className="eyebrow">THE LIBRARY</p>
            <h2 id="ready-title">已上线的主题</h2>
          </div>
          <span>{ready.length} 个主题 · 研究成果可读</span>
        </div>
        <div className="topic-grid">
          {ready.map((t, i) => {
            const s = summary(t.slug);
            return (
              <a
                key={t.slug}
                className={"topic-card tone-" + t.slug}
                href={routeHash({ slug: t.slug })}
              >
                <div className="topic-card-top">
                  <span className="topic-index">
                    {String(i + 1).padStart(2, "0")}
                  </span>
                  <span className="topic-domain">
                    {domainName(t.domain_id)}
                  </span>
                  <span aria-hidden="true">↗</span>
                </div>
                <h3>{t.title}</h3>
                <p>{t.description}</p>
                <div className="topic-count">
                  <strong>{s.count}</strong>
                  <span>
                    项可能性 <span aria-hidden="true">/</span> {s.groups}{" "}
                    个用途分组
                  </span>
                </div>
                <div className="topic-card-bottom">
                  <span>资料截点 {s.researchDate}</span>
                  <span>
                    {s.proposed
                      ? `${s.proposed} 项待验证`
                      : "来源支持，未必实测"}
                  </span>
                </div>
              </a>
            );
          })}
        </div>
        {!ready.length && (
          <Empty title="当前条件下没有已上线主题">
            <p>研究计划会单独显示在下方。</p>
          </Empty>
        )}
      </section>
      <aside className="reading-note">
        <span aria-hidden="true">↳</span>
        <div>
          <strong>先理解边界，再提出需求。</strong>
          <p>
            来源支持不等于运行实测。每一项结果都保留必要条件、组件依赖与原文证据；结构校验也不代表独立人工验收。
          </p>
        </div>
      </aside>
      <section className="plans" aria-labelledby="plans-title">
        <div className="section-heading">
          <div>
            <p className="eyebrow">ON THE RESEARCH DESK</p>
            <h2 id="plans-title">研究计划</h2>
          </div>
          <span>{planned.length} 个方向 · 尚无可能性地图</span>
        </div>
        <p className="muted">
          以下是拟研究的主题，介绍的是研究范围，不代表能力已经被确认。
        </p>
        <div className="plans-grid">
          {planned.map((t) => (
            <a
              href={routeHash({ slug: t.slug })}
              className="plan-card"
              key={t.slug}
            >
              <div>
                <span className="plan-status">待研究</span>
                <span>{domainName(t.domain_id)}</span>
              </div>
              <h3>
                {t.title}
                <span aria-hidden="true"> →</span>
              </h3>
              <p>{t.description}</p>
            </a>
          ))}
        </div>
        {!planned.length && <p className="muted">当前条件下没有研究计划。</p>}
      </section>
    </div>
  );
}
function Planned({ topic }: { topic: Topic }) {
  return (
    <div className="planned-page">
      <a href="#/">← 返回图书馆</a>
      <p className="eyebrow">RESEARCH PLAN</p>
      <span className="plan-status">待研究 · 尚未上线</span>
      <h1>{topic.title}</h1>
      <p className="lead">{topic.description}</p>
      <dl>
        <div>
          <dt>所属领域</dt>
          <dd>{domainName(topic.domain_id)}</dd>
        </div>
        <div>
          <dt>研究优先级</dt>
          <dd>{topic.priority}</dd>
        </div>
      </dl>
      <p>
        此主题目前只有研究计划，尚无可能性条目、来源或研究报告。研究成果纳入仓库后，才会随静态构建发布。
      </p>
      <a className="primary-button" href="#/">
        浏览已有研究 →
      </a>
    </div>
  );
}
function CopyGoal({
  topic,
  p,
  sources,
}: {
  topic: string;
  p: Possibility;
  sources: Source[];
}) {
  const [state, setState] = useState<"idle" | "done" | "manual">("idle");
  const area = useRef<HTMLTextAreaElement>(null);
  const value = goalText(topic, p, sources);
  useEffect(() => {
    setState("idle");
  }, [p.id]);
  useEffect(() => {
    if (state === "manual") {
      area.current?.focus();
      area.current?.select();
    }
  }, [state]);
  async function copy() {
    try {
      if (!navigator.clipboard) throw new Error("Clipboard unavailable");
      await navigator.clipboard.writeText(value);
      setState("done");
    } catch {
      setState("manual");
    }
  }
  return (
    <div className="copy-goal">
      <button className="primary-button" onClick={copy}>
        {state === "done" ? "已复制目标 ✓" : "复制需求描述"}
        <span aria-hidden="true"> ↗</span>
      </button>
      <p>包含结果、前提和来源，仅复制文字。</p>
      <span className="sr-only" role="status">
        {state === "done" ? "目标描述已复制到剪贴板" : ""}
      </span>
      {state === "manual" && (
        <div className="manual-copy">
          <label htmlFor="manual-goal">
            自动复制不可用。请选中下方文字手动复制。
          </label>
          <textarea
            id="manual-goal"
            ref={area}
            readOnly
            value={value}
            rows={10}
          />
        </div>
      )}
    </div>
  );
}
function SourceCard({
  source,
  quotes,
}: {
  source: Source;
  quotes?: { quote: string; location?: string }[];
}) {
  return (
    <article className="source-card" id={"source-" + source.id}>
      <div className="source-card-label">
        <span>{source.id}</span>
        <span>{source.source_class || source.source_type || "来源"}</span>
      </div>
      <h3>
        <External url={source.url}>{source.title}</External>
      </h3>
      <p className="source-url">{source.url}</p>
      {quotes?.length ? (
        quotes.map((q, i) => (
          <div key={i}>
            <blockquote>{q.quote}</blockquote>
            {q.location && (
              <p className="source-location">原文位置：{q.location}</p>
            )}
          </div>
        ))
      ) : (
        <>
          <blockquote>{source.evidence}</blockquote>
          {source.location && (
            <p className="source-location">原文位置：{source.location}</p>
          )}
        </>
      )}
      <details>
        <summary>查看来源记录</summary>
        <pre>{JSON.stringify(source, null, 2)}</pre>
      </details>
    </article>
  );
}
function Detail({
  map,
  p,
  slug,
  revision,
  onClose,
}: {
  map: AtlasMap;
  p: Possibility;
  slug: string;
  revision: string;
  onClose: () => void;
}) {
  const heading = useRef<HTMLHeadingElement>(null);
  useEffect(() => {
    if (window.matchMedia("(max-width: 899px)").matches) {
      heading.current?.focus();
      window.scrollTo({ top: 0 });
    }
  }, [p.id]);
  const related = map.sources.filter((s) => p.source_ids.includes(s.id));
  const extras: Record<string, string> = {
    version_basis: "版本依据",
    version_requirements: "版本要求",
    verification_limit: "验证范围",
    evidence_basis: "证据性质",
    example: "示例与案例",
    routes: "实现路线",
  };
  return (
    <section
      className={"detail " + (p.status === "proposed" ? "proposed-detail" : "")}
      aria-label="可能性详情"
    >
      <div className="detail-top">
        <a className="back-list" href={routeHash({ slug })}>
          ← 返回列表
        </a>
        <span>阅读详情</span>
        <button className="text-button desktop-only" onClick={onClose}>
          收起详情
        </button>
      </div>
      <div className="detail-body">
        <p className="eyebrow">{p.id}</p>
        <h2 ref={heading} tabIndex={-1}>
          {p.title}
        </h2>
        <div className="detail-badges">
          <span className="path-badge">{availabilityLabel(p)}</span>
          <Status p={p} />
        </div>
        {p.status === "proposed" && (
          <div className="proposed-notice">
            <strong>这是一项待验证方向</strong>
            <p>现有证据尚不能确认完整结果，请先阅读下方限制。</p>
          </div>
        )}
        <h3>可实现的结果</h3>
        <p className="result-text">{p.result}</p>
        <h3>条件与边界</h3>
        <p>{p.conditions || "原研究未注明条件，请先核对。"}</p>
        {p.capability_layer && (
          <div className="component-layer">
            <span>能力归属</span>
            <strong>
              {layerNames[p.capability_layer] ||
                p.capability_layer.replaceAll("_", " ")}
            </strong>
          </div>
        )}
        {p.required_components?.length ? (
          <>
            <h3>必要组件</h3>
            <ul>
              {p.required_components.map((c, i) => (
                <li key={i}>{c}</li>
              ))}
            </ul>
          </>
        ) : null}
        {p.status === "reviewed" && p.reviewed_by ? (
          <>
            <h3>人工审阅记录</h3>
            <pre>
              {typeof p.reviewed_by === "string"
                ? p.reviewed_by
                : JSON.stringify(p.reviewed_by, null, 2)}
            </pre>
          </>
        ) : null}
        <CopyGoal topic={map.topic.name} p={p} sources={map.sources} />
        <div className="detail-section-heading">
          <h3>支持这一结果的来源</h3>
          <span>{related.length} 条</span>
        </div>
        {!related.length && <p>原研究未附来源；该条目尚待验证。</p>}
        {related.map((s) => (
          <SourceCard
            key={s.id}
            source={s}
            quotes={p.evidence_refs?.filter((e) => e.source_id === s.id)}
          />
        ))}
        <a className="text-link" href={routeHash({ slug, view: "sources" })}>
          查看此主题全部来源 →
        </a>
        {Object.entries(extras).some(([key]) => p[key]) && (
          <details className="extra-record">
            <summary>更多研究记录</summary>
            {Object.entries(extras).map(([key, label]) =>
              p[key] ? (
                <div key={key}>
                  <h3>{label}</h3>
                  {typeof p[key] === "string" ? (
                    <p>{p[key] as string}</p>
                  ) : (
                    <pre>{JSON.stringify(p[key], null, 2)}</pre>
                  )}
                </div>
              ) : null,
            )}
          </details>
        )}
        <details className="extra-record">
          <summary>原始条目 JSON</summary>
          <pre>{JSON.stringify(p, null, 2)}</pre>
        </details>
        <RawLinks slug={slug} revision={revision} />
      </div>
    </section>
  );
}
function SourcesView({ bundle, route }: { bundle: Bundle; route: Route }) {
  const [q, setQ] = useState("");
  const map = bundle.map;
  const sources = map.sources.filter((s) =>
    [s.title, s.id, s.evidence, s.source_class, s.source_type]
      .join(" ")
      .toLocaleLowerCase()
      .includes(q.toLocaleLowerCase()),
  );
  useEffect(() => {
    if (route.sourceId)
      document
        .getElementById("source-" + route.sourceId)
        ?.scrollIntoView({ block: "start" });
  }, [route.sourceId]);
  return (
    <section className="sources-page">
      <div className="section-heading">
        <div>
          <p className="eyebrow">FOLLOW THE EVIDENCE</p>
          <h2>来源资料库</h2>
        </div>
        <span>
          {sources.length} / {map.sources.length} 条
        </span>
      </div>
      <p className="muted">
        短摘录保留原文。引用说明资料支持哪些结果，不代表结果已经实测。
      </p>
      <input
        className="input"
        aria-label="搜索来源"
        placeholder="查找来源名称、摘录或类型…"
        value={q}
        onChange={(e) => setQ(e.target.value)}
      />
      {route.sourceId && !map.sources.some((s) => s.id === route.sourceId) && (
        <p role="status">没有找到指定来源。</p>
      )}
      <div className="sources-grid">
        {sources.map((s) => (
          <div key={s.id}>
            <SourceCard source={s} />
            <div className="source-usages">
              <span>相关可能性</span>
              {sourceUsage(map, s.id).map((p) => (
                <a
                  key={p.id}
                  href={routeHash({ slug: bundle.slug, pid: p.id })}
                >
                  {p.title} →
                </a>
              ))}
              {!sourceUsage(map, s.id).length && (
                <p>主题范围、版本或边界的背景来源。</p>
              )}
              <a
                className="source-permalink"
                href={routeHash({
                  slug: bundle.slug,
                  view: "sources",
                  sourceId: s.id,
                })}
              >
                此来源的固定链接
              </a>
            </div>
          </div>
        ))}
      </div>
      {!sources.length && <Empty title="没有匹配的来源" />}
    </section>
  );
}
function ReportView({ bundle }: { bundle: Bundle }) {
  return (
    <div className="report-layout">
      <aside className="report-toc">
        <h2>报告目录</h2>
        <nav aria-label="研究报告目录">
          {reportHeadings(bundle.markdown).map((h) => (
            <a
              key={h.id}
              href={"#" + h.id}
              onClick={(e) => {
                e.preventDefault();
                scrollReport(h.id);
              }}
            >
              {h.text}
            </a>
          ))}
        </nav>
        <RawLinks slug={bundle.slug} revision={bundle.provenance.revision} />
      </aside>
      <article className="report prose">
        <p className="report-origin">
          以下原文来自仓库 possibilities.md，保留研究方法与覆盖缺口。
        </p>
        <SafeMarkdown slug={bundle.slug} revision={bundle.provenance.revision}>
          {bundle.markdown}
        </SafeMarkdown>
        <details className="report-validation">
          <summary>查看原研究校验报告（不代表运行验收）</summary>
          <pre>{bundle.validationReport}</pre>
        </details>
      </article>
    </div>
  );
}
function TopicPage({ topic, route }: { topic: Topic; route: Route }) {
  const [bundle, setBundle] = useState<Bundle | null>(
    cache.get(topic.slug) || null,
  );
  const [error, setError] = useState("");
  const [retry, setRetry] = useState(0);
  const [hideNav, setHideNav] = useState(false);
  const [hideDetail, setHideDetail] = useState(false);
  const drawer = useRef<HTMLDialogElement>(null);
  useEffect(() => {
    let alive = true;
    const abort = new AbortController();
    setError("");
    setBundle(cache.get(topic.slug) || null);
    if (!cache.has(topic.slug))
      fetch(
        `${import.meta.env.BASE_URL}content/${encodeURIComponent(topic.slug)}.json`,
        { signal: abort.signal },
      )
        .then((r) => {
          if (!r.ok) throw new Error("无法载入静态内容");
          return r.json();
        })
        .then((b: Bundle) => {
          if (!b.map?.possibilities || !b.markdown)
            throw new Error("内容格式不正确");
          cache.set(topic.slug, b);
          if (alive) setBundle(b);
        })
        .catch((e) => {
          if (alive && e.name !== "AbortError")
            setError("静态研究文件未能载入。请重试，或打开仓库原文。");
        });
    return () => {
      alive = false;
      abort.abort();
    };
  }, [topic.slug, retry]);
  useEffect(() => setHideDetail(false), [route.pid]);
  const s = summary(topic.slug);
  function update(patch: Partial<Route>) {
    navigate({ ...route, ...patch, pid: undefined }, true);
  }
  if (error)
    return (
      <div className="planned-page">
        <h1>内容暂时无法载入</h1>
        <p role="alert">{error}</p>
        <button
          className="primary-button"
          onClick={() => setRetry((v) => v + 1)}
        >
          重新加载
        </button>
        <RawLinks slug={topic.slug} revision={library.revision} />
      </div>
    );
  if (!bundle)
    return (
      <div className="loading" role="status">
        正在打开 {topic.title} 的研究地图…
      </div>
    );
  const map = bundle.map;
  const filtered = filterPs(map.possibilities, route);
  const supported = filtered.filter((p) => p.status !== "proposed");
  const proposed = filtered.filter((p) => p.status === "proposed");
  const selected = route.pid
    ? map.possibilities.find((p) => p.id === route.pid)
    : supported[0] || proposed[0];
  const groupLinks = (
    <>
      <button
        className={!route.group ? "selected" : ""}
        onClick={() => {
          update({ group: "" });
          drawer.current?.close();
        }}
      >
        <span>全部可能性</span>
        <span>{map.possibilities.length}</span>
      </button>
      {map.groups.map((g) => (
        <button
          key={g.id}
          className={route.group === g.id ? "selected" : ""}
          onClick={() => {
            update({ group: g.id });
            drawer.current?.close();
          }}
        >
          <span>{g.name}</span>
          <span>
            {map.possibilities.filter((p) => p.group_ids.includes(g.id)).length}
          </span>
        </button>
      ))}
    </>
  );
  return (
    <div className="topic-shell">
      <div className="topic-heading">
        <div>
          <a className="breadcrumb" href="#/">
            图书馆
          </a>
          <span className="breadcrumb"> / {domainName(topic.domain_id)}</span>
          <h1>{topic.title}</h1>
          <p>{topic.description}</p>
        </div>
        <div className="topic-stats">
          <strong>
            {s.count}
            <span> 项可能性</span>
          </strong>
          <span>
            {s.groups} 个用途分组 · 资料截点 {s.researchDate}
          </span>
          <span>
            {s.supported} 项来源支持
            {s.proposed ? ` · ${s.proposed} 项待验证` : ""}
          </span>
        </div>
      </div>
      <div className="topic-tabs">
        <nav aria-label="主题视图">
          <a
            aria-current={route.view === "map" ? "page" : undefined}
            href={routeHash({ slug: topic.slug })}
          >
            可能性地图
          </a>
          <a
            aria-current={route.view === "report" ? "page" : undefined}
            href={routeHash({ slug: topic.slug, view: "report" })}
          >
            研究报告
          </a>
          <a
            aria-current={route.view === "sources" ? "page" : undefined}
            href={routeHash({ slug: topic.slug, view: "sources" })}
          >
            来源 <span>{map.sources.length}</span>
          </a>
        </nav>
        <External
          url={githubFile(
            topic.slug,
            "possibilities.json",
            bundle.provenance.revision,
          )}
        >
          仓库原文
        </External>
      </div>
      {route.view === "report" ? (
        <ReportView bundle={bundle} />
      ) : route.view === "sources" ? (
        <SourcesView bundle={bundle} route={route} />
      ) : (
        <>
          <div className="browser-toolbar">
            <button
              className="secondary-button mobile-categories"
              onClick={() => drawer.current?.showModal()}
            >
              ☰ 用途分类
            </button>
            <button
              className="text-button desktop-only"
              aria-expanded={!hideNav}
              onClick={() => setHideNav((v) => !v)}
            >
              {hideNav ? "展开分类" : "收起分类"}
            </button>
            <div className="topic-search">
              <span aria-hidden="true">⌕</span>
              <input
                aria-label="在当前主题中搜索"
                placeholder="搜索结果、别名、关键词…"
                value={route.q}
                onChange={(e) => update({ q: e.target.value })}
              />
            </div>
            <Filters route={route} update={update} />
            {hideDetail && (
              <button
                className="text-button desktop-only"
                onClick={() => setHideDetail(false)}
              >
                展开详情
              </button>
            )}
          </div>
          <dialog
            className="category-drawer"
            ref={drawer}
            aria-label="用途分类"
          >
            <div>
              <h2>用途分类</h2>
              <button
                aria-label="关闭分类"
                onClick={() => drawer.current?.close()}
              >
                ×
              </button>
            </div>
            <nav aria-label="移动用途分类">{groupLinks}</nav>
          </dialog>
          <div
            className={
              "browser-layout " +
              (hideNav ? "no-nav " : "") +
              (hideDetail ? "no-detail " : "") +
              (route.pid ? "mobile-detail" : "")
            }
          >
            {!hideNav && (
              <aside className="group-nav">
                <p className="eyebrow">按用途探索</p>
                <nav aria-label="用途分类">{groupLinks}</nav>
                <p className="nav-note">
                  分类用于导航。一个 P 可以出现在多个分组，条目与详情保持唯一。
                </p>
                <details>
                  <summary>研究覆盖与缺口</summary>
                  <ul>
                    {map.coverage_gaps.map((g, i) => (
                      <li key={i}>{g}</li>
                    ))}
                  </ul>
                </details>
              </aside>
            )}
            <section className="p-list" aria-label="可能性列表">
              <div className="list-heading">
                <h2>
                  {map.groups.find((g) => g.id === route.group)?.name ||
                    "全部可能性"}
                </h2>
                <span role="status">{filtered.length} 项</span>
              </div>
              {route.group && !map.groups.some((g) => g.id === route.group) && (
                <p>未找到指定分类，请重置筛选。</p>
              )}
              {supported.length > 0 && (
                <>
                  <p className="list-section-label">
                    有来源支持 <span>{supported.length}</span>
                  </p>
                  {supported.map((p) => (
                    <PLink
                      key={p.id}
                      p={p}
                      slug={topic.slug}
                      active={selected?.id === p.id}
                      query={route.q}
                      route={route}
                    />
                  ))}
                </>
              )}
              {proposed.length > 0 && (
                <section className="proposed-list" aria-label="待验证方向">
                  <h2>
                    待验证方向 <span>{proposed.length}</span>
                  </h2>
                  <p>完整结果尚未确认，请先阅读限制。</p>
                  {proposed.map((p) => (
                    <PLink
                      key={p.id}
                      p={p}
                      slug={topic.slug}
                      active={selected?.id === p.id}
                      query={route.q}
                      route={route}
                    />
                  ))}
                </section>
              )}
              {!filtered.length && (
                <Empty title="没有匹配的可能性">
                  <p>可以换一个关键词，或重置筛选。</p>
                  <button
                    className="text-button"
                    onClick={() => update({ ...blankRoute, slug: topic.slug })}
                  >
                    清除全部条件
                  </button>
                </Empty>
              )}
            </section>
            {!hideDetail &&
              (selected ? (
                <Detail
                  key={selected.id}
                  map={map}
                  p={selected}
                  slug={topic.slug}
                  revision={bundle.provenance.revision}
                  onClose={() => setHideDetail(true)}
                />
              ) : (
                <section className="detail empty">
                  <h2>{route.pid ? "没有找到这个 P" : "选择一项可能性"}</h2>
                  <p>
                    {route.pid
                      ? "该链接的 ID 不在当前研究中。"
                      : "浏览列表，查看结果、条件和原文依据。"}
                  </p>
                  {route.pid && (
                    <a href={routeHash({ slug: topic.slug })}>返回全部可能性</a>
                  )}
                </section>
              ))}
          </div>
        </>
      )}
    </div>
  );
}
export function App() {
  const [route, setRoute] = useState(() => parseRoute(window.location.hash));
  const [globalQ, setGlobalQ] = useState("");
  useEffect(() => {
    const handler = () => setRoute(parseRoute(window.location.hash));
    window.addEventListener("hashchange", handler);
    return () => window.removeEventListener("hashchange", handler);
  }, []);
  const topic = library.catalog.topics.find((t) => t.slug === route.slug);
  useEffect(() => {
    document.title = topic
      ? `${topic.title} · P Atlas`
      : "P Atlas · 可能性图书馆";
  }, [topic]);
  return (
    <>
      <a
        href="#main-content"
        className="skip-link"
        onClick={(e) => {
          e.preventDefault();
          document.getElementById("main-content")?.focus();
        }}
      >
        跳到正文
      </a>
      <header className="site-header">
        <a className="brand" href="#/">
          <span className="brand-mark" aria-hidden="true">
            P<span>↗</span>
          </span>
          <span>
            <strong>P Atlas</strong>
            <small>可能性图书馆</small>
          </span>
        </a>
        <nav aria-label="主导航">
          <a href="#/" aria-current={!route.slug ? "page" : undefined}>
            主题图书馆
          </a>
          <External url="https://github.com/liamamilin/COP/tree/proposal/cop-capability-map-v0">
            GitHub
          </External>
        </nav>
        <form
          className="header-search"
          role="search"
          aria-label="全站搜索"
          onSubmit={(e) => {
            e.preventDefault();
            navigate({ q: globalQ });
          }}
        >
          <label className="sr-only" htmlFor="global-q">
            站内搜索
          </label>
          <input
            id="global-q"
            value={globalQ}
            onChange={(e) => setGlobalQ(e.target.value)}
            placeholder="搜索整个图书馆"
          />
          <button aria-label="搜索整个图书馆">⌕</button>
        </form>
        <span className="edition">
          READING EDITION <strong>0.1</strong>
        </span>
      </header>
      <main id="main-content" tabIndex={-1}>
        {route.invalid || (route.slug && !topic) ? (
          <div className="planned-page">
            <h1>没有找到这个页面</h1>
            <p>链接可能不完整，或该主题尚未进入目录。</p>
            <a href="#/">返回图书馆</a>
          </div>
        ) : topic ? (
          topic.status === "planned" ? (
            <Planned topic={topic} />
          ) : (
            <TopicPage key={topic.slug} topic={topic} route={route} />
          )
        ) : (
          <LibraryPage route={route} />
        )}
      </main>
      <footer className="site-footer">
        <span>
          P Atlas <span className="muted">/ 从结果出发，循来源探索。</span>
        </span>
        <span>
          仓库内容快照 ·{" "}
          <External
            url={`https://github.com/liamamilin/COP/commit/${library.revision}`}
          >
            {library.revision.slice(0, 7)}
          </External>
        </span>
      </footer>
    </>
  );
}
