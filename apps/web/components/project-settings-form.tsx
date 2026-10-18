"use client";

import { useRouter } from "next/navigation";
import { type FormEvent, useState } from "react";

import { publicApiBaseUrl, type ProjectSettingsView, type ProjectSummary } from "../lib/api";

/**
 * Project Settings.
 *
 * Two distinct things live here and are kept apart on purpose:
 *
 *   project metadata   title, domain, scope, description
 *   generation settings language, depth, densities, practice mode
 *
 * The generation block is a project-level *override*, not a second copy of the
 * app defaults. Every control is labelled with where its value currently comes
 * from, because a user who changes one and sees no difference has no way to tell
 * an override from a default that happens to match.
 */
export function ProjectSettingsForm({
  project,
  effective,
}: {
  project: ProjectSummary;
  effective: ProjectSettingsView;
}) {
  // Drives which lifecycle action is offered. Reading it from the project rather
  // than from the route matters: an archived project is still reachable by URL,
  // and the only action that makes sense there is Restore.
  const archived = project.status === "archived";
  const router = useRouter();
  const [pending, setPending] = useState(false);
  const [message, setMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const generation = effective.effective.generation;
  const overridden = new Set(Object.keys(effective.overrides.generation ?? {}));

  async function saveMetadata(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setPending(true);
    setMessage(null);
    setError(null);
    const data = new FormData(event.currentTarget);
    const response = await fetch(`${publicApiBaseUrl()}/projects/${project.id}`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        title: data.get("title"),
        domain: data.get("domain"),
        scope: data.get("scope"),
        description: data.get("description"),
        preferred_language: data.get("preferred_language"),
      }),
    });
    setPending(false);
    if (response.ok) {
      setMessage("Saved");
      router.refresh();
    } else {
      setError("Unable to save project settings");
    }
  }

  async function saveGeneration(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setPending(true);
    setMessage(null);
    setError(null);
    const data = new FormData(event.currentTarget);
    const response = await fetch(`${publicApiBaseUrl()}/projects/${project.id}/settings`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        generation: {
          language: data.get("language"),
          generation_depth: data.get("generation_depth"),
          learner_level: data.get("learner_level"),
          detail_density: data.get("detail_density"),
          evidence_density: data.get("evidence_density"),
          practice_mode: data.get("practice_mode"),
        },
      }),
    });
    setPending(false);
    if (response.ok) {
      setMessage("Generation settings saved. They apply to the next run.");
      router.refresh();
    } else {
      setError("Unable to save generation settings");
    }
  }

  async function clearOverrides() {
    setPending(true);
    const response = await fetch(`${publicApiBaseUrl()}/projects/${project.id}/settings`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ reset: ["generation"] }),
    });
    setPending(false);
    if (response.ok) {
      setMessage("Cleared. This project now follows the app defaults.");
      router.refresh();
    } else {
      setError("Unable to clear overrides");
    }
  }

  async function archive() {
    if (
      !window.confirm(
        "Archive this project?\n\nIt leaves the active list, but every source, published version, and learning record is kept. You can restore it from the home page.",
      )
    ) {
      return;
    }
    setPending(true);
    const response = await fetch(`${publicApiBaseUrl()}/projects/${project.id}`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ status: "archived" }),
    });
    if (response.ok) router.push("/");
    else {
      setPending(false);
      setMessage("Unable to archive project");
    }
  }

  async function restore() {
    setPending(true);
    const response = await fetch(`${publicApiBaseUrl()}/projects/${project.id}/restore`, {
      method: "POST",
    });
    if (response.ok) {
      setMessage("Restored. This project is back in the active list.");
      router.refresh();
    } else {
      setMessage("Unable to restore project");
    }
    setPending(false);
  }

  /**
   * Delete removes the project from every list. It is a status change rather
   * than a row removal, but the user is told plainly that it cannot be undone
   * from the UI, because that is the difference from Archive and conflating the
   * two is how people lose work they meant to keep.
   */
  async function remove() {
    if (
      !window.confirm(
        "Delete this project?\n\nThis is different from archiving: it will not appear anywhere in COP Studio, including the archived list, and there is no restore. The stored data is left on disk but unreachable from the app.\n\nArchive instead if you may want it back.",
      )
    ) {
      return;
    }
    setPending(true);
    const response = await fetch(`${publicApiBaseUrl()}/projects/${project.id}`, {
      method: "DELETE",
    });
    if (response.ok) router.push("/");
    else {
      setPending(false);
      setMessage("Unable to delete project");
    }
  }

  return (
    <div className="settings-stack">
      <form className="editor-form" onSubmit={saveMetadata}>
        <p className="eyebrow">PROJECT</p>
        <label>
          <span>Project title</span>
          <input name="title" defaultValue={project.title} required />
        </label>
        <label>
          <span>Domain</span>
          <input name="domain" defaultValue={project.domain} required />
        </label>
        <label>
          <span>Scope</span>
          <textarea name="scope" defaultValue={project.scope} rows={4} />
        </label>
        <label>
          <span>Target outcome / description</span>
          <textarea name="description" defaultValue={project.description} rows={4} />
        </label>
        {message && (
          <p className="form-message" role="status">
            {message}
          </p>
        )}
        {error && (
          <p className="form-error" role="alert">
            {error}
          </p>
        )}
        <button className="primary-button" disabled={pending} type="submit">
          {pending ? "Saving…" : "Save project details"}
        </button>
      </form>

      <form className="editor-form" onSubmit={saveGeneration}>
        <p className="eyebrow">GENERATION OVERRIDES</p>
        <p className="muted-note">
          These apply to this project only and take priority over the app defaults. A single run
          can still override them.
        </p>
        <label>
          <span>
            Output language{" "}
            {overridden.has("language") ? <em className="override-mark">project override</em> : null}
          </span>
          <select name="language" defaultValue={generation.language}>
            <option value="auto">Auto (follow the source material)</option>
            <option value="zh-CN">中文</option>
            <option value="en">English</option>
            <option value="ja">日本語</option>
          </select>
        </label>
        <label>
          <span>
            Generation depth{" "}
            {overridden.has("generation_depth") ? (
              <em className="override-mark">project override</em>
            ) : null}
          </span>
          <select name="generation_depth" defaultValue={generation.generation_depth}>
            <option value="fast">Fast — a short, focused process</option>
            <option value="standard">Standard — the default breadth</option>
            <option value="deep">Deep — more Goals and Stages</option>
          </select>
        </label>
        <label>
          <span>
            Learner level{" "}
            {overridden.has("learner_level") ? (
              <em className="override-mark">project override</em>
            ) : null}
          </span>
          <select name="learner_level" defaultValue={generation.learner_level}>
            <option value="new">New to this domain</option>
            <option value="some_experience">Some experience</option>
            <option value="advanced">Advanced</option>
          </select>
        </label>
        <label>
          <span>
            Detail density{" "}
            {overridden.has("detail_density") ? (
              <em className="override-mark">project override</em>
            ) : null}
          </span>
          <select name="detail_density" defaultValue={generation.detail_density}>
            <option value="compact">Compact — one step per Stage</option>
            <option value="balanced">Balanced</option>
            <option value="detailed">Detailed — up to four steps per Stage</option>
          </select>
        </label>
        <label>
          <span>
            Evidence density{" "}
            {overridden.has("evidence_density") ? (
              <em className="override-mark">project override</em>
            ) : null}
          </span>
          <select name="evidence_density" defaultValue={generation.evidence_density}>
            <option value="minimal">Minimal — one citation per Stage</option>
            <option value="key_claims">Key claims</option>
            <option value="high">High — cite generously</option>
          </select>
        </label>
        <label>
          <span>
            Practice mode{" "}
            {overridden.has("practice_mode") ? (
              <em className="override-mark">project override</em>
            ) : null}
          </span>
          <select name="practice_mode" defaultValue={generation.practice_mode}>
            <option value="priority">Priority — practices for the first processes</option>
            <option value="all">All — a practice per process</option>
            <option value="off">Off — no practices</option>
          </select>
        </label>
        {overridden.size > 0 && (
          <button disabled={pending} onClick={clearOverrides} type="button">
            Clear overrides and follow app defaults
          </button>
        )}
        <button className="primary-button" disabled={pending} type="submit">
          {pending ? "Saving…" : "Save generation overrides"}
        </button>
      </form>

      <section className="danger-zone">
        <p className="eyebrow">PROJECT LIFECYCLE</p>
        <h3>{archived ? "This project is archived" : "Archive or delete"}</h3>
        {archived ? (
          <p>
            It is hidden from the active list. Every source, published version, and learning record
            is still here.
          </p>
        ) : (
          <p>
            <strong>Archive</strong> keeps everything and can be undone from the home page.{" "}
            <strong>Delete</strong> cannot be undone from the app.
          </p>
        )}
        <div className="danger-actions">
          {archived ? (
            <button disabled={pending} onClick={restore} type="button">
              Restore this project
            </button>
          ) : (
            <>
              <button disabled={pending} onClick={archive} type="button">
                Archive this project
              </button>
              <button className="danger-button" disabled={pending} onClick={remove} type="button">
                Delete permanently
              </button>
            </>
          )}
        </div>
      </section>
    </div>
  );
}
