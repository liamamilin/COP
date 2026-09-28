import type { Page } from "@playwright/test";

import { API_URL } from "./fixtures";

/**
 * Set the app-level mock scenario, and restore it afterwards.
 *
 * The mock's `slow` and `rate_limit` scenarios are the only deterministic way
 * to keep a run open long enough to watch the stream, cancel it mid-flight, or
 * drop the connection. Using the `success` path alone would make every test
 * race a run that finishes in under a second.
 */
export async function setMockScenario(scenario: string): Promise<void> {
  const response = await fetch(`${API_URL}/settings`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ provider: { type: "mock", mock_scenario: scenario } }),
  });
  if (!response.ok) {
    throw new Error(`could not set mock scenario to ${scenario}: HTTP ${response.status}`);
  }
}

export async function resetMockScenario(): Promise<void> {
  await setMockScenario("success").catch(() => undefined);
}

/** Create a project with no version, which is the state that shows the Harness. */
export async function createProject(title: string): Promise<string> {
  const response = await fetch(`${API_URL}/projects`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ title, domain: title, scope: "SSE verification" }),
  });
  if (!response.ok) throw new Error(`project create failed: ${response.status}`);
  return ((await response.json()) as { id: string }).id;
}

/** Soft-delete test projects so the development library stays clean. */
export async function deleteProject(projectId: string): Promise<void> {
  await fetch(`${API_URL}/projects/${projectId}`, { method: "DELETE" }).catch(
    () => undefined,
  );
}

/**
 * Record every SSE frame the page receives.
 *
 * Installed before the run starts, because the interesting behaviour is what
 * arrives over the stream: which event types, whether `id:` is present so a
 * reconnect can resume, and whether a dropped connection resumes from where it
 * left off instead of replaying from zero.
 */
export async function recordStreamEvents(page: Page): Promise<void> {
  await page.evaluate(() => {
    const w = window as unknown as { __sse: string[] };
    w.__sse = [];
    const Original = window.EventSource;
    class Recording extends Original {
      constructor(url: string | URL, init?: EventSourceInit) {
        super(url, init);
        const record = (type: string) => (event: Event) => {
          const message = event as MessageEvent<string>;
          const id = message.lastEventId || "-";
          w.__sse.push(`${type}#${id}#${message.data.slice(0, 60)}`);
        };
        for (const type of [
          "step.started",
          "step.completed",
          "step.warning",
          "run.started",
          "run.resumed",
          "run.queued",
          "run.completed",
          "run.failed",
          "run.cancelled",
          "run.needs_attention",
        ]) {
          this.addEventListener(type, record(type));
        }
        this.addEventListener("open", () => w.__sse.push("open#-#"));
        this.addEventListener("error", () => w.__sse.push("error#-#"));
      }
    }
    window.EventSource = Recording as unknown as typeof EventSource;
  });
}

export async function streamEvents(page: Page): Promise<string[]> {
  return page.evaluate(
    () => (window as unknown as { __sse: string[] }).__sse ?? [],
  );
}
