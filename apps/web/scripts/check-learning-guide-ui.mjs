// Isolated reader interaction regression. Every document and PUT is mocked.
import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import { createRequire } from "node:module";
import { fileURLToPath } from "node:url";
import { chromium } from "@playwright/test";

const require = createRequire(import.meta.url);
const vitestRequire = createRequire(require.resolve("vitest/package.json"));
const { build } = createRequire(vitestRequire.resolve("vite"))("esbuild");
const artifact = JSON.parse(await readFile(new URL("../../../fixtures/langchain-basic-cop.json", import.meta.url), "utf8"));
const goal = artifact.goals[0];
const learningProcess = artifact.main_processes[0];
const foundation = artifact.shared_foundations.find((item) => item.id === learningProcess.start.ref);
const progress = {
  project_id: "p", version_id: "frozen-v1", version_number: 1, completed_goals: 0, total_goals: 1,
  foundations: foundation.stage_refs.map((stage_id) => ({ stage_id, status: "not_started", updated_at: null })),
  goals: [{ goal_id: goal.id, title: goal.title, completed: false, completed_stages: 0,
    total_stages: learningProcess.stage_refs.length, blocked_by: [], practice: null,
    stages: learningProcess.stage_refs.map((stage_id) => ({ stage_id, status: "not_started", notes: null, updated_at: null })),
  }],
};
const bundled = await build({
  stdin: {
    contents: `import React from 'react';
      import { createRoot } from 'react-dom/client';
      import artifact from '../../fixtures/langchain-basic-cop.json';
      import { LearnView } from './components/learn-view';
      import { ProjectShell } from './components/project-shell';
      const query = new URLSearchParams(location.search);
      const progress = window.TEST_PROGRESS;
      const project = {id:'p',title:'A guided learning plan'};
      const version = {id:progress.version_id,version_number:1,created_by:'user'};
      createRoot(document.getElementById('root')).render(<ProjectShell project={project} version={version} artifact={artifact} active="learn">
        <div className="content-wrap"><LearnView projectId="p" artifact={artifact} progress={progress} selectedGoalId={artifact.goals[0].id} selectedStageId={query.get('stage') || undefined} sources={{}} /></div>
      </ProjectShell>);`,
    resolveDir: fileURLToPath(new URL("../", import.meta.url)), loader: "tsx",
  },
  bundle: true, write: false, outdir: "/virtual", format: "iife", jsx: "automatic",
  define: { "process.env.NODE_ENV": '"test"', "process.env.NEXT_PUBLIC_API_BASE_URL": '"/api/v1"', "process.env.INTERNAL_API_BASE_URL": "undefined" },
  plugins: [{ name: "isolated-next", setup(builder) {
    builder.onResolve({ filter: /^next\/(link|navigation)$/ }, ({ path }) => ({ path, namespace: "fixture" }));
    builder.onLoad({ filter: /.*/, namespace: "fixture" }, ({ path }) => ({
      contents: path.endsWith("navigation") ? "export function useRouter() { return {refresh(){}}; }" : "import React from 'react'; export default function Link(props) { return React.createElement('a',props,props.children); }",
      loader: "js", resolveDir: fileURLToPath(new URL("../", import.meta.url)),
    }));
  } }],
});
const css = await readFile(new URL("../app/globals.css", import.meta.url), "utf8")
  + bundled.outputFiles.filter((file) => file.path.endsWith(".css")).map((file) => file.text).join("\n");
const js = bundled.outputFiles.find((file) => file.path.endsWith(".js")).text;
const browser = await chromium.launch({ channel: process.env.PLAYWRIGHT_CHANNEL || undefined });
try {
  const page = await browser.newPage({ viewport: { width: 1440, height: 1000 } });
  const errors = [];
  const writes = [];
  let rejectWrite = false;
  page.on("pageerror", (error) => errors.push(error.message));
  page.on("console", (message) => {
    // The rejected-write case deliberately returns 503; no other console error
    // (including React hydration/rendering diagnostics) is expected.
    if (message.type() === "error" && !message.text().includes("503")) errors.push(message.text());
  });
  await page.route("**/*", async (route) => {
    const request = route.request();
    const url = new URL(request.url());
    assert.equal(url.origin, "http://reader.test", "No live services may be contacted");
    if (request.method() === "GET" && url.pathname === "/projects/p/learn") {
      return route.fulfill({ contentType: "text/html", body: `<!doctype html><html data-theme="light"><head><meta name="viewport" content="width=device-width,initial-scale=1"><style>${css}</style></head><body><div id="root"></div><script>window.TEST_PROGRESS=${JSON.stringify(progress)};</script><script>${js}</script></body></html>` });
    }
    if (request.method() === "PUT" && url.pathname === "/api/v1/projects/p/learning-progress") {
      const body = request.postDataJSON();
      writes.push(body);
      if (rejectWrite) return route.fulfill({ status: 503, json: { detail: "Saved progress unavailable" } });
      const row = body.kind === "foundation" ? progress.foundations.find((item) => item.stage_id === body.stage_id)
        : progress.goals[0].stages.find((item) => item.stage_id === body.stage_id);
      assert.ok(row, "Only existing activity ids may be written");
      row.status = body.status;
      return route.fulfill({ json: { ...body } });
    }
    throw new Error(`Unexpected request: ${request.method()} ${url.href}`);
  });
  const firstId = foundation.stage_refs[0];
  const href = (stage) => `http://reader.test/projects/p/learn?goal=${goal.id}&version=frozen-v1${stage ? `&stage=${stage}` : ""}`;
  await page.goto(href());
  await page.locator(".learn-current-stage-title").waitFor();
  assert.equal(await page.locator(".learn-current-stage-title").innerText(), artifact.stages.find((s) => s.id === firstId).title);
  assert.equal(await page.locator(".learn-stage").count(), learningProcess.stage_refs.length, "Full main line remains available");
  const reader = page.locator(".learn-detail");
  await reader.locator('[data-guide-section="instructions"] .detail-item').first().waitFor();
  assert.equal(await reader.locator('[data-guide-section="background"]').getAttribute("open"), null);
  await reader.locator(".step-reference > summary").click();
  await reader.locator(".step-reference .concept-inline").first().waitFor();
  await reader.locator(".step-reference > summary").click();
  await reader.getByRole("link", { name: "Next", exact: true }).click();
  await page.waitForURL(`**stage=${foundation.stage_refs[1]}#current-step`);
  assert.equal(writes.length, 0, "Viewing and navigating must not record progress");
  await page.goto(href(firstId));
  await reader.getByRole("button", { name: "Mark complete", exact: true }).click();
  await reader.getByRole("button", { name: "Reopen stage", exact: true }).waitFor();
  assert.equal(writes.length, 1);
  assert.equal(writes[0].kind, "foundation");
  assert.equal(writes[0].goal_id, "");
  assert.equal(writes[0].version_id, "frozen-v1");
  await page.reload();
  await reader.getByRole("button", { name: "Reopen stage", exact: true }).waitFor();

  await page.goto(href(learningProcess.stage_refs[1]));
  const stageTitle = artifact.stages.find((s) => s.id === learningProcess.stage_refs[1]).title;
  await page.getByRole("heading", { name: stageTitle, exact: true }).waitFor();
  await reader.getByRole("button", { name: "Mark complete", exact: true }).click();
  await reader.getByRole("button", { name: "Reopen stage", exact: true }).waitFor();
  assert.equal(writes[1].kind, "stage");
  assert.equal(writes[1].stage_id, learningProcess.stage_refs[1]);
  assert.equal(writes[1].goal_id, goal.id);
  assert.equal(writes[1].version_id, "frozen-v1");
  rejectWrite = true;
  await reader.getByRole("button", { name: "Reopen stage", exact: true }).click();
  await page.getByRole("alert").waitFor();
  await reader.getByRole("button", { name: "Reopen stage", exact: true }).waitFor();
  assert.equal(progress.goals[0].stages[1].status, "completed", "Failed write rolls back instead of pretending success");

  await page.setViewportSize({ width: 390, height: 844 });
  assert.ok(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth), "Reader fits mobile");
  const positions = await page.evaluate(() => ({ reader: document.querySelector(".learn-detail").getBoundingClientRect().top, route: document.querySelector(".learn-mainline").getBoundingClientRect().top }));
  assert.ok(positions.reader < positions.route, "Mobile places the active instructions before the long route");
  assert.deepEqual(errors, []);
  console.log("Browser PASS: foundation-first guidance, read-only navigation, frozen-version foundation/stage completion, persistence, failed-write rollback, mobile reader order.");
} finally { await browser.close(); }
