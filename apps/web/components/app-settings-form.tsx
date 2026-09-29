"use client";

import { type FormEvent, useState } from "react";

import { publicApiBaseUrl, type AppSettings } from "../lib/api";

export function AppSettingsForm({ initial }: { initial: AppSettings }) {
  const [settings, setSettings] = useState(initial);
  const [providerType, setProviderType] = useState(initial.provider.type);
  const [pending, setPending] = useState(false);
  const [message, setMessage] = useState<string | null>(null);

  async function save(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setPending(true);
    setMessage(null);
    const data = new FormData(event.currentTarget);
    const response = await fetch(`${publicApiBaseUrl()}/settings`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        provider: {
          type: providerType,
          base_url: data.get("base_url"),
          api_key: data.get("api_key"),
          model: data.get("model"),
          timeout: Number(data.get("timeout")),
          max_retries: Number(data.get("max_retries")),
          mock_scenario: data.get("mock_scenario"),
        },
        generation: {
          language: data.get("language"),
          generation_depth: data.get("generation_depth"),
          learner_level: data.get("learner_level"),
          detail_density: data.get("detail_density"),
          practice_mode: data.get("practice_mode"),
          evidence_density: data.get("evidence_density"),
        },
        appearance: { theme: data.get("theme"), density: data.get("density") },
      }),
    });
    setPending(false);
    if (!response.ok) { setMessage("Unable to save settings"); return; }
    const updated = (await response.json()) as AppSettings;
    setSettings(updated);
    document.documentElement.dataset.theme = updated.appearance.theme;
    document.documentElement.dataset.density = updated.appearance.density;
    setMessage("Settings saved. Secrets remain encrypted and masked.");
  }

  async function testConnection() {
    setPending(true);
    setMessage("Testing saved provider…");
    const response = await fetch(`${publicApiBaseUrl()}/settings/provider/test`, { method: "POST" });
    const body = (await response.json().catch(() => null)) as { provider?: string; detail?: unknown } | null;
    setPending(false);
    setMessage(response.ok ? `${body?.provider === "mock" ? "Mock Provider" : "Provider"} connection succeeded.` : `Connection failed: ${JSON.stringify(body?.detail ?? "unknown error")}`);
  }

  return <form className="settings-form" onSubmit={save}>
    <section className="settings-section"><div className="settings-copy"><p className="eyebrow">AI PROVIDER</p><h2>Model connection</h2><p>Mock mode works without a secret. Live keys are encrypted before database storage and never returned to the browser.</p></div><div className="settings-fields">
      <label><span>Provider</span><select name="provider_type" value={providerType} onChange={(event) => setProviderType(event.target.value as typeof providerType)}><option value="mock">Mock Provider</option><option value="openai_compatible">OpenAI Compatible</option></select></label>
      {providerType === "mock" ? <label><span>Mock scenario</span><select name="mock_scenario" defaultValue={settings.provider.mock_scenario}><option value="success">Success</option><option value="invalid">Invalid structured output</option><option value="timeout">Timeout</option><option value="rate_limit">Rate limit</option><option value="slow">Slow generation</option></select></label> : <>
        <label><span>Base URL</span><input name="base_url" type="url" defaultValue={settings.provider.base_url} placeholder="https://api.example.com/v1" required /></label>
        <label><span>API key {settings.provider.has_api_key && <b>{settings.provider.api_key_hint ?? "stored"}</b>}</span><input name="api_key" type="password" placeholder={settings.provider.has_api_key ? "Leave blank to keep stored key" : "Required"} /></label>
        <label><span>Model</span><input name="model" defaultValue={settings.provider.model} placeholder="model-name" required /></label>
      </>}
      <div className="form-row"><label><span>Timeout (seconds)</span><input name="timeout" type="number" min="5" max="600" defaultValue={settings.provider.timeout} /></label><label><span>Max retries</span><input name="max_retries" type="number" min="0" max="5" defaultValue={settings.provider.max_retries} /></label></div>
      <input name="base_url" type="hidden" value={providerType === "mock" ? "" : undefined} disabled={providerType !== "mock"} />
      <input name="model" type="hidden" value={providerType === "mock" ? "" : undefined} disabled={providerType !== "mock"} />
      <input name="api_key" type="hidden" value="" disabled={providerType !== "mock"} />
      <input name="mock_scenario" type="hidden" value="success" disabled={providerType === "mock"} />
      <button className="secondary-button" disabled={pending} onClick={testConnection} type="button">Test saved connection</button>
    </div></section>

    <section className="settings-section"><div className="settings-copy"><p className="eyebrow">GENERATION DEFAULTS</p><h2>Useful by default</h2><p>Run overrides still take precedence over project and app settings.</p></div><div className="settings-fields">
      <label><span>Language</span><select name="language" defaultValue={settings.generation.language}><option value="auto">Auto</option><option value="zh-CN">Chinese</option><option value="en">English</option></select></label>
      <label><span>Depth</span><select name="generation_depth" defaultValue={settings.generation.generation_depth}><option value="fast">Fast</option><option value="standard">Standard</option><option value="deep">Deep</option></select></label>
      <label><span>Learner level</span><select name="learner_level" defaultValue={settings.generation.learner_level}><option value="new">New to domain</option><option value="some_experience">Some experience</option><option value="advanced">Advanced</option></select></label>
      <label><span>Detail density</span><select name="detail_density" defaultValue={settings.generation.detail_density}><option value="compact">Compact</option><option value="balanced">Balanced</option><option value="detailed">Detailed</option></select></label>
      <div className="form-row"><label><span>Practices</span><select name="practice_mode" defaultValue={settings.generation.practice_mode}><option value="off">Off</option><option value="priority">Priority processes</option><option value="all">All processes</option></select></label><label><span>Evidence</span><select name="evidence_density" defaultValue={settings.generation.evidence_density}><option value="minimal">Minimal</option><option value="key_claims">Key claims</option><option value="high">High</option></select></label></div>
    </div></section>

    <section className="settings-section"><div className="settings-copy"><p className="eyebrow">APPEARANCE</p><h2>Reading environment</h2></div><div className="settings-fields"><label><span>Theme</span><select name="theme" defaultValue={settings.appearance.theme}><option value="system">System</option><option value="light">Light</option><option value="dark">Dark</option></select></label><label><span>Density</span><select name="density" defaultValue={settings.appearance.density}><option value="comfortable">Comfortable</option><option value="compact">Compact</option></select></label></div></section>
    {message && <p className="settings-message" role="status">{message}</p>}
    <button className="primary-button settings-save" disabled={pending} type="submit">{pending ? "Working…" : "Save settings"}</button>
  </form>;
}
