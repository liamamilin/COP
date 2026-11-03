// Isolated learning-unit reader. All documents are local fixtures; every request is blocked.
import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import { createRequire } from "node:module";
import { fileURLToPath } from "node:url";
import { chromium } from "@playwright/test";

const require = createRequire(import.meta.url);
const vitestRequire = createRequire(require.resolve("vitest/package.json"));
const { build } = createRequire(vitestRequire.resolve("vite"))("esbuild");
const communication = process.argv.includes("--communication");
const fixture = communication ? "communication-basics" : "langchain-basic";
const lesson = JSON.parse(await readFile(new URL(`../../../fixtures/${fixture}-learning-unit.json`, import.meta.url), "utf8"));
const bundled = await build({
  stdin: {
    contents: `import React from 'react';
      import { createRoot } from 'react-dom/client';
      import artifact from '../../fixtures/${fixture}-cop.json';
      import unit from '../../fixtures/${fixture}-learning-unit.json';
      import manifest from '../../fixtures/${fixture}-learning-unit.manifest.json';
      import { LearningUnitReader } from './components/learning-unit-reader';
      const mismatch = new URLSearchParams(location.search).has('mismatch');
      createRoot(document.getElementById('root')).render(
        <LearningUnitReader artifact={artifact} unit={unit} unitHash={manifest.unit_sha256} bindingValid={!mismatch} />
      );`,
    resolveDir: fileURLToPath(new URL("../", import.meta.url)), loader: "tsx",
  },
  bundle: true, write: false, outdir: "/virtual", format: "iife", jsx: "automatic",
  define: { "process.env.NODE_ENV": '"test"', "process.env.NEXT_PUBLIC_API_BASE_URL": '"/api/v1"', "process.env.INTERNAL_API_BASE_URL": "undefined" },
});
const css = await readFile(new URL("../app/globals.css", import.meta.url), "utf8")
  + bundled.outputFiles.filter((file) => file.path.endsWith(".css")).map((file) => file.text).join("\n");
const js = bundled.outputFiles.find((file) => file.path.endsWith(".js")).text;
const browser = await chromium.launch({ channel: process.env.PLAYWRIGHT_CHANNEL || undefined });
try {
  const page = await browser.newPage({ viewport: { width: 1440, height: 1000 }, acceptDownloads: true });
  const errors = [];
  const requests = [];
  page.on("pageerror", (error) => errors.push(error.message));
  page.on("console", (message) => { if (message.type() === "error") errors.push(message.text()); });
  await page.route("**/*", (route) => {
    const url = new URL(route.request().url());
    requests.push(`${route.request().method()} ${url.pathname}`);
    if (url.origin !== "http://unit.test" || url.pathname !== "/") {
      return route.abort("blockedbyclient");
    }
    return route.fulfill({
      contentType: "text/html",
      body: `<!doctype html><html><head><meta name="viewport" content="width=device-width,initial-scale=1"><style>${css}</style></head><body><div id="root"></div><script>${js}</script></body></html>`,
    });
  });

  await page.goto("http://unit.test/");
  if (communication) {
    await page.getByRole("heading", { name: lesson.title, exact: true }).waitFor();
    const orientation = page.locator("[data-teaching-orientation]");
    assert.ok((await orientation.innerText()).includes(lesson.orientation.question));
    assert.ok((await orientation.innerText()).includes(lesson.orientation.case_unknowns[0]));
    for (let index = 0; index < lesson.steps.length; index++) {
      await page.getByRole("button", { name: new RegExp(`Step ${index + 1}`) }).click();
      const trace = page.locator("[data-reasoning-walkthrough]");
      await trace.waitFor();
      assert.ok((await trace.innerText()).includes(lesson.steps[index].reasoning[0].warrant));
      assert.ok((await trace.innerText()).includes(lesson.steps[index].reasoning[0].limitation));
      assert.equal(await page.locator("[data-bound-method] pre").count(), 0, "Non-code learning must not require shell commands");
      const order = await page.evaluate(() => ({
        trace: document.querySelector("[data-reasoning-walkthrough]").getBoundingClientRect().top,
        method: document.querySelector("[data-bound-method]").getBoundingClientRect().top,
      }));
      assert.ok(order.trace < order.method, "Reasoning must precede the method");
    }
    await page.getByRole("button", { name: /Step 1/ }).click();
    const question = page.locator(`section[aria-labelledby="question-${lesson.steps[0].practice.id}"]`);
    await question.getByLabel("Your response", { exact: true }).fill("这是推测，材料不足以确认对方的动机。");
    await question.getByRole("button", { name: /Show next hint/ }).click();
    assert.equal(await question.locator("ol li").count(), 1);
    await page.getByRole("button", { name: "Save on this device" }).click();
    await page.getByText("Saved on this device · unverified self-report", { exact: true }).waitFor();
    await page.reload();
    await page.getByRole("button", { name: "Load saved notes" }).click();
    await page.getByText("Loaded saved notes · unverified self-report", { exact: true }).waitFor();
    assert.equal(await question.getByLabel("Your response", { exact: true }).inputValue(), "这是推测，材料不足以确认对方的动机。");
    await page.getByRole("button", { name: /Step 2/ }).click();
    await page.getByRole("button", { name: /Step 1/ }).click();
    assert.equal(await question.getByLabel("Your response", { exact: true }).inputValue(), "这是推测，材料不足以确认对方的动机。");
    await page.getByRole("button", { name: "Explain, diagnose & transfer" }).click();
    assert.equal(await page.getByRole("button", { name: "Mark complete", exact: true }).count(), 0);
    for (const question of lesson.assessment) {
      await page.getByRole("heading", { name: question.prompt, exact: true }).waitFor();
    }
    for (const width of [390, 760, 1440]) {
      await page.setViewportSize({ width, height: 1000 });
      assert.ok(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth + 1));
    }
    await page.goto("http://unit.test/?mismatch");
    await page.getByText("Lesson revision mismatch").waitFor();
    assert.deepEqual(errors, []);
    assert.deepEqual(requests.filter((item) => item !== "GET /"), []);
    console.log("Browser PASS: communication route rationale, evidence→inference→limits before methods, no shell, graduated support, local notes, assessment, responsive widths; no API/provider writes.");
  } else {
  await page.getByRole("heading", { name: /从显式配置到一次可检查的 Agent 回复/ }).waitFor();
  assert.ok((await page.locator("header").innerText()).includes("hand-authored teaching sample"));
  assert.equal(await page.getByText("LESSON REVISION MISMATCH", { exact: false }).count(), 0);
  // Partial path is the default and says so without implying Goal completion.
  await page.getByText("Partial goal · not full capability evidence").waitFor();
  assert.equal(await page.getByRole("button", { name: "Mark complete", exact: true }).count(), 0);

  // Method bodies come from the bound artifact, not duplicated in the unit.
  const artifactStage = JSON.parse(await readFile(new URL("../../../fixtures/langchain-basic-cop.json", import.meta.url), "utf8")).stages[0];
  await page.locator("[data-bound-method]").first().waitFor();
  assert.ok((await page.locator("[data-bound-method]").first().innerText()).includes(artifactStage.implementation_details[0].command.split("\n")[0]));

  // No hidden concept: its explanation and causal chain precede the method.
  const positions = await page.evaluate(() => ({
    concepts: [...document.querySelectorAll("h3")].find((h) => h.textContent === "Understand the ideas")?.getBoundingClientRect().top,
    methods: [...document.querySelectorAll("h3")].find((h) => h.textContent === "Follow the method")?.getBoundingClientRect().top,
    checks: [...document.querySelectorAll("h3")].find((h) => h.textContent === "Outputs & checks")?.getBoundingClientRect().top,
  }));
  assert.ok(positions.concepts < positions.methods && positions.methods < positions.checks);

  // Practice: hints and criteria are revealed on demand, recorded as support used.
  const practice = page.locator("section").filter({ has: page.getByText("PREDICT · UNGRADED") }).last();
  await practice.getByRole("button", { name: /Show next hint/ }).click();
  assert.equal(await practice.locator("ol li").count(), 1);
  await practice.getByRole("button", { name: "Show review criteria" }).click();
  await practice.getByText("Review criteria · not an answer grade").waitFor();
  await practice.locator("textarea").first().fill("I will check sys.executable first.");
  await practice.locator("textarea").nth(1).fill("No outside help yet.");

  // Observed result is local evidence, not completion.
  await page.getByLabel("Observed result / mismatch").fill("imports ok");
  await page.getByRole("button", { name: "Save on this device" }).click();
  await page.getByText("Saved on this device · unverified self-report").waitFor();
  await page.reload();
  await page.getByRole("button", { name: "Load saved notes" }).click();
  await page.getByText("Loaded saved notes · unverified self-report").waitFor();
  assert.equal(await page.getByLabel("Observed result / mismatch").inputValue(), "imports ok");
  const restored = page.locator("section").filter({ has: page.getByText("PREDICT · UNGRADED") }).last();
  assert.equal(await restored.locator("textarea").first().inputValue(), "I will check sys.executable first.");
  assert.equal(await restored.locator("textarea").first().screenshot === undefined, false);

  // Provider-only route exposes paid/network boundary and its extra method, never calling it.
  await page.getByLabel("Learning path").selectOption("provider");
  await page.getByText("Full task path · results still need verification").waitFor();
  await page.getByText("Cost: possible; separate explicit consent required before any paid command").waitFor();
  await page.getByRole("button", { name: /Step 4/ }).click();
  await page.getByText("真实能力路径：有凭据且同意费用后").waitFor();
  const providerRequests = requests.filter((item) => !item.startsWith("GET /"));
  assert.deepEqual(providerRequests, []);

  // Assessment is ungraded; opening it does not mark anything.
  await page.getByRole("button", { name: "Explain, diagnose & transfer" }).click();
  await page.getByText("SELF-REPORT, NOT A GRADE").waitFor();
  assert.ok(await page.getByRole("heading", { name: "ASSESSMENT · SELF-REPORT, NOT A GRADE" }).count() === 0);
  assert.ok((await page.locator("article").innerText()).includes("the application does not determine whether your answer is correct"));
  assert.equal(await page.getByText(/mastered|passed|score/i).count(), 0);

  // Export contains only local self-reports and can be re-imported.
  const downloadPromise = page.waitForEvent("download");
  await page.getByRole("button", { name: "Export notes" }).click();
  const download = await downloadPromise;
  const exported = await readFile(await download.path(), "utf8");
  assert.ok(exported.includes('"scope": "unverified-self-report"'));
  assert.ok(!exported.includes("LC_API_KEY"));
  assert.ok(!exported.includes("mastery"));
  await page.getByLabel("Import notes").setInputFiles({ name: "notes.json", mimeType: "application/json", buffer: Buffer.from(exported) });
  await page.getByText("Imported notes · not saved on this device yet").waitFor();

  // Wrong revision fails closed.
  await page.goto("http://unit.test/?mismatch");
  await page.getByText("Lesson revision mismatch").waitFor();
  assert.equal(await page.getByText("Follow the method").count(), 0);

  // Mobile reader puts instructions before the route and fits without overflow.
  await page.goto("http://unit.test/");
  await page.setViewportSize({ width: 390, height: 844 });
  const overflow = await page.evaluate(() => [...document.querySelectorAll("body *")].filter((el) => el.getBoundingClientRect().right > innerWidth + 1).slice(0, 12).map((el) => `${el.tagName}.${el.className} ${Math.round(el.getBoundingClientRect().right)} :: ${el.textContent?.slice(0, 60)}`));
  assert.ok(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth + 1), overflow.join("\n"));
  const mobile = await page.evaluate(() => ({
    lesson: document.querySelector("article")?.getBoundingClientRect().top,
    route: document.querySelector("nav")?.getBoundingClientRect().top,
  }));
  assert.ok(mobile.lesson < mobile.route);
  await page.setViewportSize({ width: 1440, height: 1000 });
  assert.deepEqual(errors, []);
  assert.deepEqual(requests.filter((item) => item !== "GET /"), []);
  console.log("Browser PASS: bound methods, concept→method→check order, graduated support, local save/reload/export/import, path-specific work, ungraded assessment, fail-closed revision, mobile order, no writes or provider calls.");
  }
} finally {
  await browser.close();
}
