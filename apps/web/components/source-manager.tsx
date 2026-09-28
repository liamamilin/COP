"use client";

import { type FormEvent, useState } from "react";

import { publicApiBaseUrl, type SourceSummary } from "../lib/api";

type AddMode = "text" | "upload" | "url";

export function SourceManager({ projectId, initialSources }: { projectId: string; initialSources: SourceSummary[] }) {
  const [sources, setSources] = useState(initialSources);
  const [mode, setMode] = useState<AddMode>("text");
  const [pending, setPending] = useState(false);
  const [error, setError] = useState<string | null>(null);

  function upsert(source: SourceSummary) {
    setSources((current) => [source, ...current.filter((item) => item.id !== source.id)]);
  }

  async function parseResponse(response: Response): Promise<SourceSummary> {
    if (!response.ok) {
      const payload = (await response.json().catch(() => null)) as { detail?: string } | null;
      throw new Error(payload?.detail ?? "Source processing failed");
    }
    return (await response.json()) as SourceSummary;
  }

  async function addText(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setPending(true);
    setError(null);
    const form = event.currentTarget;
    const data = new FormData(form);
    try {
      const source = await parseResponse(await fetch(`${publicApiBaseUrl()}/projects/${projectId}/sources/text`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ title: data.get("title"), text: data.get("text"), format: data.get("format") }),
      }));
      upsert(source);
      form.reset();
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "Source processing failed");
    } finally { setPending(false); }
  }

  async function addUpload(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setPending(true);
    setError(null);
    const form = event.currentTarget;
    try {
      const source = await parseResponse(await fetch(`${publicApiBaseUrl()}/projects/${projectId}/sources/upload`, { method: "POST", body: new FormData(form) }));
      upsert(source);
      form.reset();
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "Upload failed");
    } finally { setPending(false); }
  }

  async function addUrl(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setPending(true);
    setError(null);
    const form = event.currentTarget;
    const data = new FormData(form);
    try {
      const source = await parseResponse(await fetch(`${publicApiBaseUrl()}/projects/${projectId}/sources/url`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ url: data.get("url"), title: data.get("title") || null }),
      }));
      upsert(source);
      form.reset();
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "URL processing failed");
    } finally { setPending(false); }
  }

  async function reprocess(sourceId: string) {
    setPending(true);
    setError(null);
    try {
      upsert(await parseResponse(await fetch(`${publicApiBaseUrl()}/sources/${sourceId}/reprocess`, { method: "POST" })));
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "Retry failed");
    } finally { setPending(false); }
  }

  async function remove(sourceId: string) {
    if (!window.confirm("Delete this source? Published COP versions will not be changed.")) return;
    const response = await fetch(`${publicApiBaseUrl()}/sources/${sourceId}`, { method: "DELETE" });
    if (response.ok) setSources((current) => current.filter((item) => item.id !== sourceId));
    else setError("Unable to delete source");
  }

  return (
    <div className="source-manager">
      <section className="source-composer">
        <div className="mode-tabs" role="tablist" aria-label="Source type">
          {(["text", "upload", "url"] as const).map((item) => (
            <button className={mode === item ? "active" : ""} key={item} onClick={() => setMode(item)} role="tab" aria-selected={mode === item} type="button">
              {item === "text" ? "Paste text" : item === "upload" ? "Upload file" : "Add URL"}
            </button>
          ))}
        </div>

        {mode === "text" && <form className="source-form" onSubmit={addText}>
          <div className="form-row"><label><span>Title</span><input name="title" required placeholder="Source title" /></label><label><span>Format</span><select name="format"><option value="text">Plain text</option><option value="markdown">Markdown</option></select></label></div>
          <label><span>Content</span><textarea name="text" required rows={8} placeholder="Paste documentation, notes, or source material…" /></label>
          <button className="primary-button" disabled={pending} type="submit">{pending ? "Processing…" : "Add text source"}</button>
        </form>}

        {mode === "upload" && <form className="source-form" onSubmit={addUpload}>
          <label><span>Display title (optional)</span><input name="title" placeholder="Uses filename when empty" /></label>
          <label className="file-drop"><span>TXT · Markdown · PDF up to 20 MB</span><input name="file" type="file" required accept=".txt,.md,.markdown,.pdf,text/plain,text/markdown,application/pdf" /></label>
          <button className="primary-button" disabled={pending} type="submit">{pending ? "Extracting…" : "Upload and extract"}</button>
        </form>}

        {mode === "url" && <form className="source-form" onSubmit={addUrl}>
          <label><span>Public HTTP/HTTPS URL</span><input name="url" type="url" required placeholder="https://example.com/guide" /></label>
          <label><span>Display title (optional)</span><input name="title" placeholder="Uses the hostname when empty" /></label>
          <button className="primary-button" disabled={pending} type="submit">{pending ? "Fetching…" : "Fetch URL"}</button>
        </form>}
        {error && <p className="form-error" role="alert">{error}</p>}
      </section>

      <section className="source-library">
        <div className="section-title-row"><div><p className="eyebrow">SOURCE LIBRARY</p><h2>{sources.length} attached sources</h2></div><p>Extracted text remains available after restart and can be inspected before generation.</p></div>
        {sources.length === 0 ? <div className="source-empty">No sources yet. Topic-only generation remains possible; sources add evidence and constraints.</div> : (
          <div className="source-list">{sources.map((source) => <article className="source-row" key={source.id}>
            <div className={`source-type ${source.type}`}>{source.type.slice(0, 3).toUpperCase()}</div>
            <div className="source-body"><div className="source-title-line"><h3>{source.title}</h3><span className={`source-status ${source.status}`}>{source.status}</span></div>
              {source.original_uri && <a href={source.original_uri} rel="noreferrer" target="_blank">{source.original_uri}</a>}
              {source.preview && <p>{source.preview}</p>}
              {source.status === "failed" && <p className="source-error">{String(source.metadata.error ?? "Extraction failed")}</p>}
              <small>{source.char_count ? `${source.char_count.toLocaleString()} characters` : "No extracted text"}</small>
            </div>
            <div className="source-actions">{source.status === "failed" && <button disabled={pending} onClick={() => reprocess(source.id)} type="button">Retry</button>}<button onClick={() => remove(source.id)} type="button">Delete</button></div>
          </article>)}</div>
        )}
      </section>
    </div>
  );
}

