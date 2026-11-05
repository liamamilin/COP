// Isolated browser regression: real React component, intercepted HTTP/SSE only.
// No running API, database, user credentials, or paid provider is accessed.
import assert from "node:assert/strict";
import { createRequire } from "node:module";
import { readFile } from "node:fs/promises";
import { fileURLToPath } from "node:url";
import { launchChrome } from "./safe-browser.mjs";

// Reuse the bundler already shipped with Vitest/Vite, without a new dependency.
const require = createRequire(import.meta.url);
const vitestRequire = createRequire(require.resolve("vitest/package.json"));
const viteRequire = createRequire(vitestRequire.resolve("vite"));
const { build } = viteRequire("esbuild");
const result = await build({
  stdin: {
    contents: `import React from 'react';
      import { createRoot } from 'react-dom/client';
      import { GenerationPanel } from './components/generation-panel';
      import { GenerationSection } from './components/generation-section';
      let notified = 0;
      const Component = new URLSearchParams(location.search).has('handoff') ? GenerationSection : GenerationPanel;
      createRoot(document.getElementById('root')).render(<Component
        projectId="project-test" topic="Read CSV" scopeHint="" sourceIds={[]}
        effective={{language:'en',generation_depth:'fast',learner_level:'new',detail_density:'balanced',evidence_density:'key_claims',practice_mode:'priority'}}
        onCandidateReady={() => { document.getElementById('candidate').textContent = String(++notified); }}
      />);`,
    resolveDir: fileURLToPath(new URL("../", import.meta.url)), loader: "tsx",
  },
  bundle: true, write: false, format: "iife", jsx: "automatic",
  define: { "process.env.NODE_ENV": '"test"', "process.env.NEXT_PUBLIC_API_BASE_URL": '"/api/v1"',
    "process.env.INTERNAL_API_BASE_URL": "undefined" },
  plugins: [{ name: "isolated-router", setup(builder) {
    builder.onResolve({ filter: /^next\/navigation$/ }, () => ({ path: "router", namespace: "fixture" }));
    builder.onLoad({ filter: /.*/, namespace: "fixture" }, () => ({
      contents: "const router = { refresh() {} }; export function useRouter() { return router; }", loader: "js",
    }));
  } }],
});
const css = await readFile(new URL("../app/globals.css", import.meta.url), "utf8");
const html = `<!doctype html><html><head><meta name="viewport" content="width=device-width,initial-scale=1"><style>${css}</style></head><body><main style="max-width:800px;margin:40px auto;padding:24px"><div id="root"></div><div id="candidate">0</div></main><script>${result.outputFiles[0].text}</script></body></html>`;
const browser = await launchChrome();
const page = await browser.newPage();
const errors = [];
page.on("pageerror", (e) => errors.push(e.message));
try {
  let state = "failed";
  let resumes = 0;
  let newRuns = 0;
  let progressReads = 0;
  let savedBody;
  let handoffCase = "created";
  let draftRequests = 0;
  const draft = () => ({ id: "draft-test", project_id: "project-test",
    source_run_id: handoffCase === "older" ? "older-run" : "run-test" });
  const run = () => ({
    id: "run-test", project_id: "project-test", status: state,
    requested_mode: "fast", metrics: {},
    error_code: state === "failed" ? "PROVIDER_TIMEOUT" : null,
    error_message: state === "failed" ? "Timeout" : null,
  });
  await page.route("http://resume.test/**", async (route) => {
    const path = new URL(route.request().url()).pathname;
    if (path === "/") return route.fulfill({ contentType: "text/html", body: html });
    if (path.includes("/drafts/from-run/")) {
      draftRequests++;
      if (handoffCase === "error") return route.fulfill({ status: 500, json: { detail: "Draft unavailable" } });
      if (handoffCase !== "created") return route.fulfill({ status: 409, json: { detail: "Draft exists" } });
      return route.fulfill({ status: 201, json: draft() });
    }
    if (path.endsWith("/draft")) return route.fulfill({ json: draft() });
    if (path.endsWith("/resume")) {
      resumes++;
      savedBody = route.request().postDataJSON();
      state = "running";
      return route.fulfill({ json: run() });
    }
    if (path.endsWith("/generation-runs")) {
      if (route.request().method() === "POST") newRuns++;
      return route.fulfill({ json: [run()] });
    }
    if (path.endsWith("/progress")) {
      progressReads++;
      return route.fulfill({ json: {
        run: run(), phases: [], candidate_available: state === "completed",
        last_event_id: resumes ? 25 : 20,
        recovery: { allowed: state === "failed", reason: "", from_step: "H60",
          completed_steps: ["H00", "H10", "H20", "H30", "H40", "H50"],
          attempt: resumes ? 2 : 1, event_cursor: resumes ? 21 : 0,
          timeout_seconds: 60,
          history: resumes ? [{ attempt: 1, error_code: "PROVIDER_TIMEOUT", error_message: "Timeout" }] : [],
        },
      } });
    }
    if (path.endsWith("/events")) {
      // Deliberately replay an OLD terminal event. It must not end observation.
      return route.fulfill({ contentType: "text/event-stream", body:
        'id: 19\nevent: run.failed\ndata: {"sequence":19}\n\n' });
    }
    throw new Error(`Unexpected request: ${path}`);
  });
  await page.goto("http://resume.test/");
  await page.getByRole("button", { name: "Resume generation", exact: true }).waitFor();
  if (process.env.RESUME_UI_SCREENSHOT) await page.screenshot({ path: process.env.RESUME_UI_SCREENSHOT, fullPage: true });
  await page.setViewportSize({ width: 390, height: 844 });
  assert.ok(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth), "mobile layout must not overflow");
  await page.getByText("Adjust request timeout", { exact: true }).click();
  await page.getByRole("spinbutton").fill("180");
  await page.getByRole("button", { name: "Resume generation", exact: true }).evaluate((button) => {
    button.click(); button.click();
  });
  await page.getByRole("button", { name: "Cancel", exact: true }).waitFor();
  assert.equal(resumes, 1, "double click must send only one resume");
  assert.deepEqual(savedBody, { expected_attempt: 1, timeout_seconds: 180 });
  const readsBefore = progressReads;
  await page.reload();
  await page.getByRole("button", { name: "Cancel", exact: true }).waitFor();
  assert.equal(resumes, 1, "refresh must observe, not execute");
  state = "completed";
  await page.locator("#candidate").filter({ hasText: "1" }).waitFor();
  assert.ok(progressReads > readsBefore, "polling must survive an old SSE failure");
  assert.equal(newRuns, 0, "resume must not create a new run");
  assert.equal(await page.locator("#candidate").textContent(), "1");
  // Browsers/proxies may reject SSE construction altogether; polling still wins.
  state = "running";
  await page.addInitScript(() => {
    window.EventSource = function Broken() { throw new Error("blocked transport"); };
  });
  await page.reload();
  await page.getByRole("button", { name: "Cancel", exact: true }).waitFor();
  state = "completed";
  await page.locator("#candidate").filter({ hasText: "1" }).waitFor();
  // The result entry must be visible without depending on router.refresh().
  for (const mode of ["created", "same", "older", "error"]) {
    handoffCase = mode;
    const before = draftRequests;
    await page.goto("http://resume.test/?handoff");
    if (mode === "error") {
      await page.getByRole("button", { name: "Retry opening draft" }).waitFor();
      handoffCase = "created";
      await page.getByRole("button", { name: "Retry opening draft" }).click();
    }
    const label = mode === "older" ? "Review existing draft ↗" : "Review draft ↗";
    const link = page.getByRole("link", { name: label, exact: true });
    await link.waitFor();
    assert.equal(await link.getAttribute("href"), "/projects/project-test/draft");
    assert.equal(draftRequests - before, mode === "error" ? 2 : 1);
    if (mode === "older") {
      await page.getByText("An earlier draft is still open.", { exact: true }).waitFor();
    }
  }
  assert.deepEqual(errors, []);
  console.log("Browser PASS: resume, reload, stale SSE, visible draft handoff, existing draft protection, opening retry.");
} catch (error) {
  console.error({ errors, body: await page.locator("body").innerText() });
  throw error;
} finally {
  await browser.close();
}
