// Synthetic settings and intercepted requests only. Never calls a real provider or API.
import assert from "node:assert/strict";
import { mkdir, readFile } from "node:fs/promises";
import { createRequire } from "node:module";
import { join } from "node:path";
import { fileURLToPath } from "node:url";
import { launchChrome } from "./safe-browser.mjs";

const require = createRequire(import.meta.url);
const vitestRequire = createRequire(require.resolve("vitest/package.json"));
const { build } = createRequire(vitestRequire.resolve("vite"))("esbuild");
const fixture = JSON.parse(await readFile(new URL("../tests/fixtures/app-settings.json", import.meta.url), "utf8"));
const bundled = await build({
  stdin: {
    contents: `import React from 'react'; import {createRoot} from 'react-dom/client';
      import {AppSettingsView} from './components/app-settings-view';
      createRoot(document.getElementById('root')).render(<AppSettingsView initial={window.TEST_SETTINGS}/>);`,
    resolveDir: fileURLToPath(new URL("../", import.meta.url)), loader: "tsx",
  },
  bundle: true, write: false, outdir: "/virtual", format: "iife", jsx: "automatic",
  define: { "process.env.NODE_ENV": '"test"', "process.env.NEXT_PUBLIC_API_BASE_URL": '"/api/v1"', "process.env.INTERNAL_API_BASE_URL": "undefined" },
  plugins: [{ name: "isolated-link", setup(builder) {
    builder.onResolve({ filter: /^next\/link$/ }, () => ({ path: "link", namespace: "fixture" }));
    builder.onLoad({ filter: /.*/, namespace: "fixture" }, () => ({
      contents: "import React from 'react'; export default function Link(props){return React.createElement('a',props,props.children)}",
      loader: "js", resolveDir: fileURLToPath(new URL("../", import.meta.url)),
    }));
  } }],
});
const css = await readFile(new URL("../app/globals.css", import.meta.url), "utf8")
  + bundled.outputFiles.filter((file) => file.path.endsWith(".css")).map((file) => file.text).join("\n");
const js = bundled.outputFiles.find((file) => file.path.endsWith(".js")).text;
const screenshots = process.env.SCREENSHOT_DIR;
if (screenshots) await mkdir(screenshots, { recursive: true });
const browser = await launchChrome();
try {
  const page = await browser.newPage({ viewport: { width: 1440, height: 1000 } });
  let initial = structuredClone(fixture), rejectSave = false;
  const calls = [], errors = [], unexpected = [];
  page.on("pageerror", (error) => errors.push(error.message));
  page.on("console", (message) => {
    if (message.type() === "error" && !message.text().includes("500")) errors.push(message.text());
  });
  await page.route("**/*", (route) => {
    const request = route.request();
    const url = new URL(request.url());
    if (url.origin !== "http://settings.test") {
      unexpected.push(request.method() + " " + url.href);
      return route.abort();
    }
    if (request.method() === "GET" && url.pathname === "/") return route.fulfill({ contentType: "text/html", body: `<!doctype html><html data-theme="${initial.appearance.theme}" data-density="${initial.appearance.density}"><head><meta name="viewport" content="width=device-width,initial-scale=1"><style>${css}</style></head><body><header class="global-header"><div class="brand"><span class="brand-mark">C</span><span><strong>COP Studio</strong><small>Operational knowledge workspace</small></span></div><div class="global-actions"><a href="#">Settings</a></div></header><div id="root"></div><script>window.TEST_SETTINGS=${JSON.stringify(initial)}</script><script>${js}</script></body></html>` });
    const body = request.postDataJSON();
    calls.push({ method: request.method(), path: url.pathname, body });
    if (request.method() === "POST" && url.pathname === "/api/v1/settings/provider/models") {
      return route.fulfill({ json: { models: ["example-alpha", "example-beta"] } });
    }
    if (request.method() === "POST" && url.pathname === "/api/v1/settings/provider/test") {
      return route.fulfill({ json: { provider: initial.provider.type === "mock" ? "mock" : "openai_compatible" } });
    }
    if (request.method() === "PATCH" && url.pathname === "/api/v1/settings") {
      if (rejectSave) return route.fulfill({ status: 500, json: { detail: "Simulated failure" } });
      const { api_key, ...provider } = body.provider;
      const updated = {
        provider: { ...initial.provider, ...provider, has_api_key: !!api_key || initial.provider.has_api_key, api_key_hint: initial.provider.api_key_hint },
        generation: body.generation, appearance: body.appearance,
      };
      return route.fulfill({ json: updated });
    }
    unexpected.push(request.method() + " " + url.href);
    return route.abort();
  });
  async function fits() {
    assert.ok(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth + 1), "Settings fit without horizontal overflow");
  }
  for (const width of [1440, 1024, 760, 390, 320]) {
    for (const scheme of ["light", "dark"]) {
      await page.setViewportSize({ width, height: 1000 });
      await page.emulateMedia({ colorScheme: scheme });
      await page.goto("http://settings.test/");
      await page.getByRole("heading", { name: "Settings", exact: true }).waitFor();
      const measured = await page.evaluate(() => ({
        h1: parseFloat(getComputedStyle(document.querySelector("main h1")).fontSize),
        h2: [...document.querySelectorAll("form h2")].map((el) => parseFloat(getComputedStyle(el).fontSize)),
        labels: [...document.querySelectorAll("form label")].map((el) => parseFloat(getComputedStyle(el).fontSize)),
        provider: document.querySelector('[name="provider_type"]').getBoundingClientRect().top,
      }));
      assert.ok(measured.h1 <= 30, "No marketing-sized heading");
      assert.ok(measured.h2.every((size) => size >= 15 && size <= 18));
      assert.ok(measured.labels.every((size) => size >= 12), "No tiny uppercase field labels");
      assert.ok(measured.provider < 550, "Settings are usable on the first screen");
      assert.equal(await page.locator("form details[open]").count(), 0);
      assert.equal(await page.getByLabel("API key", { exact: true }).inputValue(), "");
      await fits();
      if (screenshots && [1440, 390].includes(width) && scheme === "light") {
        await page.screenshot({ path: join(screenshots, `settings-${width}.png`), fullPage: width === 1440 });
      }
      await page.getByRole("link", { name: "Generation", exact: true }).click();
      assert.ok(page.url().endsWith("#settings-generation"));
    }
  }
  assert.equal(calls.length, 0, "Rendering and navigation never save or contact a provider");
  await page.setViewportSize({ width: 1440, height: 1000 });
  await page.emulateMedia({ colorScheme: "light" });
  await page.goto("http://settings.test/");
  const readForm = () => page.locator("form").evaluate((form) => Object.fromEntries(new FormData(form)));
  let values = await readForm();
  assert.equal(values.timeout, "90"); assert.equal(values.max_retries, "2");
  assert.equal(values.practice_mode, "all"); assert.equal(values.evidence_density, "high");
  await page.getByText("Advanced connection settings", { exact: true }).click();
  await page.getByLabel("Timeout (seconds)", { exact: true }).fill("120");
  await page.getByLabel("Max retries", { exact: true }).fill("4");
  await page.getByText("Advanced connection settings", { exact: true }).click();
  await page.getByText("More generation options", { exact: true }).click();
  await page.getByLabel("Practices", { exact: true }).selectOption("off");
  await page.getByLabel("Evidence", { exact: true }).selectOption("minimal");
  await page.getByText("More generation options", { exact: true }).click();
  await page.getByLabel("Base URL", { exact: true }).fill("https://edited.example/v1");
  await page.getByLabel("Model", { exact: true }).fill("edited-model");
  await page.getByRole("button", { name: "Load available models", exact: true }).click();
  await page.getByRole("status").getByText("Loaded 2 model(s). Choose one in Model.", { exact: true }).waitFor();
  assert.equal(calls.at(-1).body.base_url, "https://edited.example/v1");
  assert.equal(calls.at(-1).body.api_key, "");
  assert.deepEqual(await page.locator("datalist option").evaluateAll((options) => options.map((option) => option.value)), ["example-alpha", "example-beta"]);
  await page.getByRole("button", { name: "Test connection", exact: true }).click();
  await page.getByRole("status").getByText("Provider connection succeeded.", { exact: true }).waitFor();
  assert.equal(calls.at(-1).body.model, "edited-model");
  assert.equal(calls.filter((call) => call.method === "PATCH").length, 0);
  await page.getByLabel("Base URL", { exact: true }).fill("");
  await page.getByRole("button", { name: "Save settings", exact: true }).click();
  await page.getByRole("alert").getByText("Base URL is required for an OpenAI-compatible provider.", { exact: true }).waitFor();
  assert.equal(calls.filter((call) => call.method === "PATCH").length, 0);
  await page.getByLabel("Base URL", { exact: true }).fill("https://edited.example/v1");
  await page.getByLabel("Theme", { exact: true }).selectOption("dark");
  assert.equal(await page.locator("html").getAttribute("data-theme"), "system", "No implicit save when selecting appearance");
  await page.getByRole("button", { name: "Save settings", exact: true }).click();
  await page.getByRole("status").getByText("Settings saved. Secrets remain encrypted and masked.", { exact: true }).waitFor();
  const saved = calls.at(-1).body;
  assert.deepEqual(saved.provider, { type: "openai_compatible", base_url: "https://edited.example/v1", api_key: "", model: "edited-model", timeout: 120, max_retries: 4, mock_scenario: "success" });
  assert.equal(saved.generation.practice_mode, "off"); assert.equal(saved.generation.evidence_density, "minimal");
  assert.equal(await page.locator("html").getAttribute("data-theme"), "dark");
  assert.equal(await page.getByLabel("API key", { exact: true }).inputValue(), "");
  rejectSave = true;
  await page.getByLabel("Depth", { exact: true }).selectOption("deep");
  await page.getByRole("button", { name: "Save settings", exact: true }).click();
  await page.getByRole("alert").getByText(/Could not save settings/).waitFor();
  assert.equal(await page.getByLabel("Depth", { exact: true }).inputValue(), "deep", "Failed save retains entered values");
  rejectSave = false;
  initial = structuredClone(fixture); initial.provider.type = "mock";
  await page.goto("http://settings.test/");
  await page.getByLabel("Mock scenario", { exact: true }).waitFor();
  assert.equal(await page.getByLabel("API key", { exact: true }).count(), 0);
  values = await readForm();
  assert.equal(values.base_url, ""); assert.equal(values.model, ""); assert.equal(values.api_key, "");
  const beforeToggle = calls.length;
  await page.getByLabel("Provider", { exact: true }).selectOption("openai_compatible");
  await page.getByLabel("Base URL", { exact: true }).waitFor();
  await page.getByLabel("Provider", { exact: true }).selectOption("mock");
  assert.equal(calls.length, beforeToggle, "Provider choice alone never calls or saves anything");
  await page.getByRole("button", { name: "Save settings", exact: true }).click();
  await page.getByRole("status").getByText("Settings saved. Secrets remain encrypted and masked.", { exact: true }).waitFor();
  assert.equal(calls.at(-1).body.provider.type, "mock");
  assert.equal(calls.at(-1).body.generation.practice_mode, fixture.generation.practice_mode);
  await fits();
  assert.deepEqual(unexpected, []); assert.deepEqual(errors, []);
  console.log("Browser PASS: settings layout at 5 widths × 2 themes; labelled controls, section navigation, collapsed values retained in save payload, model list/test use entered details without saving, empty-key preservation, validation, failed-save retention, appearance and mock mode. All requests simulated; no live API/provider writes.");
} finally { await browser.close(); }
