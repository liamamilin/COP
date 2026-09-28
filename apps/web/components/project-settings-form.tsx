"use client";

import { useRouter } from "next/navigation";
import { type FormEvent, useState } from "react";

import { publicApiBaseUrl, type ProjectSummary } from "../lib/api";

export function ProjectSettingsForm({ project }: { project: ProjectSummary }) {
  const router = useRouter();
  const [pending, setPending] = useState(false);
  const [message, setMessage] = useState<string | null>(null);

  async function save(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setPending(true);
    setMessage(null);
    const data = new FormData(event.currentTarget);
    const response = await fetch(`${publicApiBaseUrl()}/projects/${project.id}`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ title: data.get("title"), domain: data.get("domain"), scope: data.get("scope"), description: data.get("description"), preferred_language: data.get("preferred_language") }),
    });
    setPending(false);
    if (response.ok) { setMessage("Saved"); router.refresh(); }
    else setMessage("Unable to save project settings");
  }

  async function archive() {
    if (!window.confirm("Archive this project? It will disappear from the active project list.")) return;
    setPending(true);
    const response = await fetch(`${publicApiBaseUrl()}/projects/${project.id}`, { method: "PATCH", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ status: "archived" }) });
    if (response.ok) router.push("/");
    else { setPending(false); setMessage("Unable to archive project"); }
  }

  return <div className="settings-stack"><form className="editor-form" onSubmit={save}>
    <label><span>Project title</span><input name="title" defaultValue={project.title} required /></label>
    <label><span>Domain</span><input name="domain" defaultValue={project.domain} required /></label>
    <label><span>Scope</span><textarea name="scope" defaultValue={project.scope} rows={4} /></label>
    <label><span>Target outcome / description</span><textarea name="description" defaultValue={project.description} rows={4} /></label>
    <label><span>Preferred language</span><select name="preferred_language" defaultValue={project.preferred_language}><option value="zh-CN">中文</option><option value="en">English</option><option value="auto">Auto</option></select></label>
    {message && <p className="form-message" role="status">{message}</p>}
    <button className="primary-button" disabled={pending} type="submit">{pending ? "Saving…" : "Save changes"}</button>
  </form><section className="danger-zone"><p className="eyebrow">DANGEROUS ACTIONS</p><h3>Archive project</h3><p>Published versions and sources remain stored locally. The project is hidden from the active list.</p><button disabled={pending} onClick={archive} type="button">Archive this project</button></section></div>;
}

