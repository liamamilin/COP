"use client";

import { useRouter } from "next/navigation";
import { type FormEvent, useState } from "react";

import { publicApiBaseUrl, type ProjectSummary } from "../lib/api";

export function NewProjectForm() {
  const router = useRouter();
  const [pending, setPending] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setPending(true);
    setError(null);
    const data = new FormData(event.currentTarget);
    const body = {
      title: String(data.get("title") ?? "").trim(),
      domain: String(data.get("title") ?? "").trim(),
      scope: String(data.get("scope") ?? "").trim(),
      description: String(data.get("outcome") ?? "").trim(),
      preferred_language: String(data.get("preferred_language") ?? "auto"),
      // Sent so the project's first run already matches what was chosen here.
      // The backend stores it as a project-level generation override, which is
      // what makes this field do anything at all.
      learner_level: String(data.get("learner_level") ?? "new"),
    };
    try {
      const response = await fetch(`${publicApiBaseUrl()}/projects`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      });
      if (!response.ok) throw new Error("Project creation failed");
      const project = (await response.json()) as ProjectSummary;
      router.push(`/projects/${project.id}/sources`);
      router.refresh();
    } catch {
      setError("无法创建项目。请确认 API 正在运行后重试。");
      setPending(false);
    }
  }

  return (
    <form className="editor-form new-project-form" onSubmit={submit}>
      <label>
        <span>What do you want to become able to do?</span>
        <input name="title" required maxLength={240} placeholder="例如：Build reliable LangChain agents" autoFocus />
      </label>
      <label>
        <span>Optional scope</span>
        <textarea name="scope" rows={3} placeholder="界定重点、技术版本或不包含的部分" />
      </label>
      <label>
        <span>Target outcome</span>
        <textarea name="outcome" rows={3} placeholder="完成后希望具备什么可验证能力？" />
      </label>
      <div className="form-row">
        <label>
          <span>Preferred language</span>
          <select name="preferred_language" defaultValue="zh-CN">
            <option value="zh-CN">中文</option>
            <option value="en">English</option>
            <option value="auto">Auto</option>
          </select>
        </label>
        <label>
          <span>Current experience</span>
          <select name="learner_level" defaultValue="new">
            <option value="new">New to this domain</option>
            <option value="some_experience">Some experience</option>
            <option value="advanced">Advanced</option>
          </select>
        </label>
      </div>
      {error && <p className="form-error" role="alert">{error}</p>}
      <button className="primary-button" disabled={pending} type="submit">
        {pending ? "Creating…" : "Create project and add sources →"}
      </button>
    </form>
  );
}

