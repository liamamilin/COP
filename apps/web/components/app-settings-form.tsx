"use client";

import { type FormEvent, type ReactNode, useId, useRef, useState } from "react";

import { publicApiBaseUrl, type AppSettings } from "../lib/api";
import styles from "./app-settings.module.css";

function Field({ id, label, hint, children }: {
  id: string; label: string; hint?: ReactNode; children: ReactNode;
}) {
  return <div className={styles.field}>
    <label htmlFor={id}>{label}</label>
    {children}
    {hint && <p id={`${id}-hint`} className={styles.hint}>{hint}</p>}
  </div>;
}

export function AppSettingsForm({ initial }: { initial: AppSettings }) {
  const formRef = useRef<HTMLFormElement>(null);
  const [settings, setSettings] = useState(initial);
  const [providerType, setProviderType] = useState(initial.provider.type);
  const [pending, setPending] = useState(false);
  const [message, setMessage] = useState<string | null>(null);
  const [failed, setFailed] = useState(false);
  const [models, setModels] = useState<string[]>([]);
  const prefix = useId();
  const id = (name: string) => `${prefix}-${name}`;

  async function save(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setPending(true);
    setMessage(null);
    setFailed(false);
    const data = new FormData(event.currentTarget);
    if (providerType === "openai_compatible" && !String(data.get("base_url") ?? "").trim()) {
      setPending(false);
      setFailed(true);
      setMessage("Base URL is required for an OpenAI-compatible provider.");
      return;
    }
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
    if (!response.ok) {
      const body = (await response.json().catch(() => null)) as { detail?: unknown } | null;
      setFailed(true);
      setMessage(`Could not save settings: ${JSON.stringify(body?.detail ?? response.status)}`);
      return;
    }
    const updated = (await response.json()) as AppSettings;
    setSettings(updated);
    document.documentElement.dataset.theme = updated.appearance.theme;
    document.documentElement.dataset.density = updated.appearance.density;
    setMessage("Settings saved. Secrets remain encrypted and masked.");
  }

  async function testConnection() {
    const form = formRef.current;
    if (!form) return;
    const data = new FormData(form);
    setPending(true);
    setFailed(false);
    setMessage("Testing the connection details above…");
    const response = await fetch(`${publicApiBaseUrl()}/settings/provider/test`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        base_url: data.get("base_url"),
        api_key: data.get("api_key"),
        model: data.get("model"),
      }),
    });
    const body = (await response.json().catch(() => null)) as { provider?: string; detail?: unknown } | null;
    setPending(false);
    setFailed(!response.ok);
    setMessage(response.ok ? `${body?.provider === "mock" ? "Mock Provider" : "Provider"} connection succeeded.` : `Connection failed: ${JSON.stringify(body?.detail ?? "unknown error")}`);
  }

  async function loadModels() {
    const form = formRef.current;
    if (!form) return;
    const data = new FormData(form);
    setPending(true);
    setFailed(false);
    setMessage("Loading models with the entered connection details…");
    const response = await fetch(`${publicApiBaseUrl()}/settings/provider/models`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ base_url: data.get("base_url"), api_key: data.get("api_key") }),
    });
    const body = (await response.json().catch(() => null)) as { models?: string[]; detail?: unknown } | null;
    setPending(false);
    if (!response.ok) {
      setFailed(true);
      setMessage(`Could not load models: ${JSON.stringify(body?.detail ?? "unknown error")}`);
      return;
    }
    const available = body?.models ?? [];
    setModels(available);
    setMessage(available.length ? `Loaded ${available.length} model(s). Choose one in Model.` : "No models were returned by the provider.");
  }

  return <form className={styles.form} onSubmit={save} ref={formRef}>
    <section id="settings-provider" className={styles.section} aria-labelledby="settings-provider-heading">
      <div className={styles.sectionHeader}>
        <div><h2 id="settings-provider-heading">Model provider</h2><p>Choose the connection used for generation. Mock mode needs no API key.</p></div>
        <span className={styles.badge}>{providerType === "mock" ? "Mock mode" : settings.provider.has_api_key ? "Key stored" : "Key not configured"}</span>
      </div>
      <div className={styles.fields}>
        <Field id={id("provider")} label="Provider">
          <select id={id("provider")} name="provider_type" value={providerType} onChange={(event) => setProviderType(event.target.value as typeof providerType)}><option value="mock">Mock Provider</option><option value="openai_compatible">OpenAI Compatible</option></select>
        </Field>
        {providerType === "mock" ? <Field id={id("scenario")} label="Mock scenario">
          <select id={id("scenario")} name="mock_scenario" defaultValue={settings.provider.mock_scenario}><option value="success">Success</option><option value="invalid">Invalid structured output</option><option value="timeout">Timeout</option><option value="rate_limit">Rate limit</option><option value="slow">Slow generation</option></select>
        </Field> : <>
          <Field id={id("url")} label="Base URL">
            <input id={id("url")} name="base_url" type="url" defaultValue={settings.provider.base_url} placeholder="https://api.example.com/v1" />
          </Field>
          <Field id={id("key")} label="API key" hint={settings.provider.has_api_key ? <>Stored key: <span className={styles.keyHint}>{settings.provider.api_key_hint ?? "masked"}</span>. Leave blank to keep it.</> : "Keys are encrypted before storage and never returned to this page."}>
            <input id={id("key")} aria-describedby={`${id("key")}-hint`} name="api_key" type="password" autoComplete="new-password" placeholder={settings.provider.has_api_key ? "Leave blank to keep stored key" : "Required"} />
          </Field>
          <Field id={id("model")} label="Model" hint="Enter a model ID, or load available models below.">
            <input id={id("model")} aria-describedby={`${id("model")}-hint`} name="model" list={id("models")} defaultValue={settings.provider.model} placeholder="Model ID" />
            <datalist id={id("models")}>{models.map((model) => <option key={model} value={model} />)}</datalist>
          </Field>
        </>}
      </div>
      <div className={styles.connectionActions}>
        <button className={styles.secondaryButton} disabled={pending} onClick={testConnection} type="button">Test connection</button>
        {providerType !== "mock" && <button className={styles.secondaryButton} disabled={pending} onClick={loadModels} type="button">Load available models</button>}
        {providerType !== "mock" && <p>Uses the entered details without saving them.</p>}
      </div>
      <details className={styles.advanced}>
        <summary>Advanced connection settings</summary>
        <div className={styles.fields}>
          <Field id={id("timeout")} label="Timeout (seconds)"><input id={id("timeout")} name="timeout" type="number" min="5" max="600" defaultValue={settings.provider.timeout} /></Field>
          <Field id={id("retries")} label="Max retries"><input id={id("retries")} name="max_retries" type="number" min="0" max="5" defaultValue={settings.provider.max_retries} /></Field>
        </div>
      </details>
      <input name="base_url" type="hidden" value="" disabled={providerType !== "mock"} />
      <input name="model" type="hidden" value="" disabled={providerType !== "mock"} />
      <input name="api_key" type="hidden" value="" disabled={providerType !== "mock"} />
      <input name="mock_scenario" type="hidden" value="success" disabled={providerType === "mock"} />
    </section>

    <section id="settings-generation" className={styles.section} aria-labelledby="settings-generation-heading">
      <div className={styles.sectionHeader}><div><h2 id="settings-generation-heading">Generation defaults</h2><p>App-wide defaults. Projects and individual runs can override these values.</p></div></div>
      <div className={styles.fields}>
        <Field id={id("language")} label="Language"><select id={id("language")} name="language" defaultValue={settings.generation.language}><option value="auto">Auto</option><option value="zh-CN">中文</option><option value="en">English</option><option value="ja">日本語</option></select></Field>
        <Field id={id("depth")} label="Depth"><select id={id("depth")} name="generation_depth" defaultValue={settings.generation.generation_depth}><option value="fast">Fast</option><option value="standard">Standard</option><option value="deep">Deep</option></select></Field>
        <Field id={id("level")} label="Learner level"><select id={id("level")} name="learner_level" defaultValue={settings.generation.learner_level}><option value="new">New to domain</option><option value="some_experience">Some experience</option><option value="advanced">Advanced</option></select></Field>
        <Field id={id("detail")} label="Detail density"><select id={id("detail")} name="detail_density" defaultValue={settings.generation.detail_density}><option value="compact">Compact</option><option value="balanced">Balanced</option><option value="detailed">Detailed</option></select></Field>
      </div>
      <details className={styles.advanced}>
        <summary>More generation options</summary>
        <div className={styles.fields}>
          <Field id={id("practice")} label="Practices"><select id={id("practice")} name="practice_mode" defaultValue={settings.generation.practice_mode}><option value="off">Off</option><option value="priority">Priority processes</option><option value="all">All processes</option></select></Field>
          <Field id={id("evidence")} label="Evidence"><select id={id("evidence")} name="evidence_density" defaultValue={settings.generation.evidence_density}><option value="minimal">Minimal</option><option value="key_claims">Key claims</option><option value="high">High</option></select></Field>
        </div>
        <p className={styles.hint}>Setting priority: run → project → app → built-in default. Saving these defaults does not rewrite published content.</p>
      </details>
    </section>

    <section id="settings-appearance" className={styles.section} aria-labelledby="settings-appearance-heading">
      <div className={styles.sectionHeader}><div><h2 id="settings-appearance-heading">Appearance</h2><p>Set the reading environment across the app.</p></div></div>
      <div className={styles.fields}>
        <Field id={id("theme")} label="Theme"><select id={id("theme")} name="theme" defaultValue={settings.appearance.theme}><option value="system">System</option><option value="light">Light</option><option value="dark">Dark</option></select></Field>
        <Field id={id("density")} label="Density"><select id={id("density")} name="density" defaultValue={settings.appearance.density}><option value="comfortable">Comfortable</option><option value="compact">Compact</option></select></Field>
      </div>
    </section>
    <div className={styles.saveBar}>
      {message ? <p className={failed ? styles.error : styles.message} role={failed ? "alert" : "status"}>{message}</p> : <p className={styles.saveHint}>Changes apply when you save.</p>}
      <button className={styles.saveButton} disabled={pending} type="submit">{pending ? "Working…" : "Save settings"}</button>
    </div>
  </form>;
}
