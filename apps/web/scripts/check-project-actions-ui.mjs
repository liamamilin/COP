// Synthetic projects and intercepted lifecycle requests only. No live API used.
import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import { createRequire } from "node:module";
import { fileURLToPath } from "node:url";
import { launchChrome } from "./safe-browser.mjs";

const require = createRequire(import.meta.url);
const vitestRequire = createRequire(require.resolve("vitest/package.json"));
const { build } = createRequire(vitestRequire.resolve("vite"))("esbuild");
const bundled = await build({
  stdin: {
    contents: `import React from 'react'; import {createRoot} from 'react-dom/client';
      import {ProjectLibrary} from './components/project-library';
      const project = {id:'p',title:'Synthetic project',scope:'A test project',latest_version:1,status:window.TEST_STATUS};
      createRoot(document.getElementById('root')).render(<ProjectLibrary active={project.status==='active'?[project]:[]} archived={project.status==='archived'?[project]:[]} />);`,
    resolveDir: fileURLToPath(new URL("../", import.meta.url)), loader: "tsx",
  },
  bundle: true, write: false, outdir: "/virtual", format: "iife", jsx: "automatic",
  define: { "process.env.NODE_ENV": '"test"', "process.env.NEXT_PUBLIC_API_BASE_URL": '"/api/v1"', "process.env.INTERNAL_API_BASE_URL": "undefined" },
  plugins: [{ name: "isolated-next-link", setup(builder) {
    builder.onResolve({ filter: /^next\/link$/ }, () => ({ path: "link", namespace: "fixture" }));
    builder.onLoad({ filter: /.*/, namespace: "fixture" }, () => ({
      contents: "import React from 'react'; export default function Link(props) { return React.createElement('a',props,props.children); }",
      loader: "js", resolveDir: fileURLToPath(new URL("../", import.meta.url)),
    }));
  } }],
});
const css = await readFile(new URL("../app/globals.css", import.meta.url), "utf8")
  + bundled.outputFiles.filter((file) => file.path.endsWith(".css")).map((file) => file.text).join("\n");
const js = bundled.outputFiles.find((file) => file.path.endsWith(".js")).text;
const browser = await launchChrome();
try {
  const page = await browser.newPage({ viewport: { width: 390, height: 844 } });
  let storedStatus = "active";
  let rejectDelete = false;
  let holdDelete = false;
  let releaseDelete;
  let observeDelete;
  let deleteGate;
  const errors = [];
  const writes = [];
  page.on("pageerror", (error) => errors.push(error.message));
  page.on("console", (message) => {
    if (message.type() === "error" && !message.text().includes("500")) errors.push(message.text());
  });
  await page.route("**/*", async (route) => {
    const request = route.request();
    const url = new URL(request.url());
    assert.equal(url.origin, "http://actions.test", "Never contact a live API");
    if (request.method() === "GET" && url.pathname === "/") return route.fulfill({
      contentType: "text/html", body: `<!doctype html><html><head><meta name="viewport" content="width=device-width,initial-scale=1"><style>${css}</style></head><body><div id="root"></div><script>window.TEST_STATUS=${JSON.stringify(storedStatus)};</script><script>${js}</script></body></html>`,
    });
    const method = request.method();
    if (url.pathname === "/api/v1/projects/p" && method === "DELETE") {
      writes.push({ method, id: "p" });
      if (rejectDelete) return route.fulfill({ status: 500, json: { detail: "Simulated failure" } });
      if (holdDelete) { observeDelete(); await deleteGate; }
      storedStatus = "deleted";
      return route.fulfill({ status: 204 });
    }
    if (url.pathname === "/api/v1/projects/p" && method === "PATCH") {
      const body = request.postDataJSON();
      writes.push({ method, body });
      assert.equal(body.status, "archived");
      storedStatus = "archived";
      return route.fulfill({ json: { status: storedStatus } });
    }
    if (url.pathname === "/api/v1/projects/p/restore" && method === "POST") {
      writes.push({ method });
      storedStatus = "active";
      return route.fulfill({ json: { status: storedStatus } });
    }
    throw new Error(`Unexpected request ${method} ${url.href}`);
  });
  const home = "http://actions.test/";
  await page.goto(home);
  const more = page.getByRole("button", { name: "Actions for Synthetic project", exact: true });
  const remove = page.getByRole("button", { name: "Delete", exact: true });
  async function choose(name) {
    await more.click();
    await page.getByRole("button", { name, exact: true }).click();
  }
  assert.equal(await remove.count(), 0, "Management controls are hidden until requested");
  await more.focus();
  await more.press("Enter");
  assert.equal(await more.getAttribute("aria-expanded"), "true");
  assert.equal(await page.getByRole("button", { name: "Archive", exact: true }).evaluate((el) => el === document.activeElement), true);
  await page.keyboard.press("Escape");
  assert.equal(await more.evaluate((el) => el === document.activeElement), true);
  assert.equal(await remove.count(), 0);
  await more.click();
  await page.getByRole("heading", { name: "Projects", exact: true }).click();
  assert.equal(await more.getAttribute("aria-expanded"), "false", "Outside click dismisses the disclosure");
  await more.click();
  await page.getByRole("link", { name: "New project", exact: true }).focus();
  assert.equal(await more.getAttribute("aria-expanded"), "false", "Moving keyboard focus away dismisses the disclosure");
  assert.equal(writes.length, 0);
  await choose("Delete");
  assert.equal(page.url(), home, "Deleting must not open the project navigation link");
  const title = page.getByRole("textbox", { name: "Type the project title to confirm" });
  assert.equal(await title.evaluate((el) => el === document.activeElement), true);
  assert.ok(await page.getByRole("button", { name: "Confirm delete", exact: true }).isDisabled());
  await title.fill("Wrong project");
  assert.ok(await page.getByRole("button", { name: "Confirm delete", exact: true }).isDisabled());
  await page.getByRole("button", { name: "Cancel", exact: true }).click();
  assert.equal(writes.length, 0);
  await choose("Delete");
  await title.press("Escape");
  assert.equal(await more.evaluate((el) => el === document.activeElement), true);
  assert.equal(writes.length, 0);

  rejectDelete = true;
  await choose("Delete");
  await title.fill("Synthetic project");
  await page.getByRole("button", { name: "Confirm delete", exact: true }).click();
  await page.getByRole("alert").waitFor();
  assert.equal(storedStatus, "active");
  assert.equal(await page.getByRole("link", { name: "Open project: Synthetic project", exact: true }).count(), 1);
  assert.equal(await title.inputValue(), "Synthetic project", "Failed request keeps confirmation and does not pretend success");
  await page.getByRole("button", { name: "Cancel", exact: true }).click();

  rejectDelete = false;
  holdDelete = true;
  deleteGate = new Promise((resolve) => { releaseDelete = resolve; });
  const seen = new Promise((resolve) => { observeDelete = resolve; });
  await choose("Delete");
  await title.fill("Synthetic project");
  await page.getByRole("button", { name: "Confirm delete", exact: true }).evaluate((button) => { button.click(); button.click(); });
  await seen;
  assert.equal(writes.filter((write) => write.method === "DELETE").length, 2, "One failed attempt plus exactly one new confirmed request");
  releaseDelete();
  await page.getByRole("heading", { name: "A place for your next learning project", exact: true }).waitFor();
  assert.equal(storedStatus, "deleted");
  assert.equal(await page.getByRole("button", { name: "Delete", exact: true }).count(), 0);

  storedStatus = "active";
  await page.goto(home);
  await choose("Archive");
  assert.equal(writes.filter((write) => write.method === "PATCH").length, 0);
  await page.getByRole("button", { name: "Confirm archive", exact: true }).click();
  await page.locator("details > summary").waitFor();
  await page.locator("details > summary").click();
  await choose("Restore");
  await page.getByRole("button", { name: "Confirm restore", exact: true }).click();
  await page.getByRole("link", { name: "Open project: Synthetic project", exact: true }).waitFor();
  assert.equal(storedStatus, "active");
  assert.equal(writes.filter((write) => write.method === "POST").length, 1);
  assert.ok(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth));
  assert.deepEqual(errors, []);
  console.log("Browser PASS: separate actions/navigation, typed-title delete, cancel/Escape, failed-write retention, duplicate-click guard, confirmed archive/restore. All writes simulated.");
} finally { await browser.close(); }
