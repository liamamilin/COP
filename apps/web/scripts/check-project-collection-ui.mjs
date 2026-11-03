// Synthetic libraries only: no real projects, APIs, provider calls, or writes.
import assert from "node:assert/strict";
import { mkdir, readFile } from "node:fs/promises";
import { createRequire } from "node:module";
import { join } from "node:path";
import { fileURLToPath } from "node:url";
import { chromium } from "@playwright/test";

const require = createRequire(import.meta.url);
const vitestRequire = createRequire(require.resolve("vitest/package.json"));
const { build } = createRequire(vitestRequire.resolve("vite"))("esbuild");
const bundled = await build({
  stdin: {
    contents: `import React from 'react'; import {createRoot} from 'react-dom/client';
      import {ProjectLibrary} from './components/project-library';
      const count = window.TEST_COUNT;
      const projects = Array.from({length:count}, (_,i)=>({
        id:'p'+i,title:i===count-1?'最后一个项目':'Project '+String(i+1).padStart(3,'0'),
        scope:'A saved project with a bounded learning path.',domain:'Learning',description:'',
        latest_version:i%3===0?null:1,status:'active',preferred_language:'en',
        updated_at:new Date(Date.UTC(2026,0,1,0,count-i)).toISOString(),
        created_at:new Date(Date.UTC(2026,0,1,0,i)).toISOString()
      }));
      const previews=Object.fromEntries(projects.filter(p=>p.latest_version!==null).slice(0,6).map(p=>[p.id,{
        summary:p.scope,stepCount:12,goals:[1,2,3,4].map(n=>({id:p.id+'g'+n,title:'Learning goal '+n}))
      }]));
      const archived=Array.from({length:window.TEST_ARCHIVED_COUNT},(_,i)=>({
        ...projects[0],id:'archive'+i,title:i===window.TEST_ARCHIVED_COUNT-1?'归档最后一个':'Archived project '+i,status:'archived'
      }));
      createRoot(document.getElementById('root')).render(<ProjectLibrary active={projects} archived={archived} previews={previews}/>);`,
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
const browser = await chromium.launch({ channel: process.env.PLAYWRIGHT_CHANNEL || undefined });
try {
  const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });
  const errors = [], unexpected = [];
  let count = 2, archivedCount = 0;
  page.on("pageerror", (error) => errors.push(error.message));
  page.on("console", (message) => { if (message.type() === "error") errors.push(message.text()); });
  await page.route("**/*", (route) => {
    const request = route.request();
    const url = new URL(request.url());
    if (request.method() !== "GET" || url.origin !== "http://collection.test" || url.pathname !== "/") {
      unexpected.push(request.method() + " " + url.href);
      return route.abort();
    }
    return route.fulfill({ contentType: "text/html", body: `<!doctype html><html><head><meta name="viewport" content="width=device-width,initial-scale=1"><style>${css}</style></head><body><div id="root"></div><script>window.TEST_COUNT=${count};window.TEST_ARCHIVED_COUNT=${archivedCount}</script><script>${js}</script></body></html>` });
  });
  const links = page.getByRole("link", { name: /^Open project:/ });
  const collection = page.locator("[data-project-collection]");
  const view = page.getByLabel("Project view", { exact: true });
  async function fits() {
    assert.ok(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth + 1), "No horizontal overflow");
  }
  for (count of [1, 2, 8, 30, 200]) {
    await page.setViewportSize({ width: 1440, height: 900 });
    await page.goto("http://collection.test/");
    await links.first().waitFor();
    assert.equal(await page.getByRole("heading", { name: "Projects", exact: true }).count(), 1);
    assert.equal(await links.count(), Math.min(count, 12));
    assert.equal(await collection.getAttribute("data-view"), count <= 4 ? "overview" : "compact");
    assert.equal(await page.getByRole("searchbox", { name: "Search projects", exact: true }).count(), count <= 4 ? 0 : 1);
    if (screenshots && [2, 8, 30].includes(count)) {
      await page.screenshot({ path: join(screenshots, `library-${count}-1440.png`), fullPage: true });
    }
    for (const width of [320, 390, 760, 1024, 1440, 1920]) {
      await page.setViewportSize({ width, height: 900 });
      await fits();
      const boxes = await links.evaluateAll((nodes) => nodes.map((node) => {
        const {x,y,width,height}=node.getBoundingClientRect(); return {x,y,width,height};
      }));
      if (width === 320) assert.ok(boxes.every((box) => Math.abs(box.x - boxes[0].x) < 1), "Phone stays single-column");
      if (width >= 1440 && count >= 8) assert.ok(boxes.filter((box) => Math.abs(box.y - boxes[0].y) < 1).length >= 3, "A large desktop library is not hardcoded to two columns");
      if (count === 1) assert.ok(boxes[0].width <= 680, "A single result does not become a screen-wide banner");
      if (screenshots && [2, 8, 30].includes(count) && width === 390) {
        await page.screenshot({ path: join(screenshots, `library-${count}-${width}.png`) });
      }
    }
    await page.setViewportSize({ width: 1440, height: 900 });
    if (count <= 4) continue;
    await view.selectOption("list");
    assert.equal(await collection.getAttribute("data-view"), "list");
    await fits();
    if (count > 12) {
      await page.getByRole("button", { name: "Next page", exact: true }).click();
      assert.equal(await links.first().getAttribute("href"), "/projects/p12");
    }
    const search = page.getByRole("searchbox", { name: "Search projects", exact: true });
    await search.fill("最后一个");
    await page.getByRole("status").getByText(`1–1 of 1 projects`, { exact: true }).waitFor();
    assert.equal(await links.count(), 1);
    assert.equal(await links.first().getAttribute("href"), `/projects/p${count - 1}`);
    assert.equal(await collection.getAttribute("data-view"), "list", "Filtering does not override the user's view");
    await search.fill("definitely-no-match");
    await page.getByRole("status").getByText("No matching projects", { exact: true }).waitFor();
    assert.equal(await links.count(), 0);
    await page.getByRole("button", { name: "Clear filters", exact: true }).click();
    await links.first().waitFor();
    assert.equal(await links.first().getAttribute("href"), "/projects/p0");
    await page.getByLabel("Sort projects", { exact: true }).selectOption("created");
    assert.equal(await links.first().getAttribute("href"), `/projects/p${count - 1}`);
    await page.getByLabel("Publication status", { exact: true }).selectOption("unpublished");
    assert.ok((await links.allInnerTexts()).every((text) => text.includes("Not published")));
    await view.selectOption("overview");
    assert.equal(await collection.getAttribute("data-view"), "overview");
    await page.setViewportSize({ width: 390, height: 900 });
    await fits();
    await view.selectOption("compact");
    await fits();
    await view.selectOption("list");
    await fits();
  }
  count = 2; archivedCount = 50;
  await page.setViewportSize({ width: 1440, height: 900 });
  await page.goto("http://collection.test/");
  const archive = page.locator("details");
  assert.equal(await archive.getAttribute("open"), null, "Archive remains collapsed");
  await archive.locator("summary").click();
  const archivedLinks = page.getByRole("link", { name: /^Open archived project:/ });
  assert.equal(await archivedLinks.count(), 12);
  assert.equal(await archive.locator("[data-project-collection]").getAttribute("data-view"), "list");
  await archive.getByRole("button", { name: "Next page", exact: true }).click();
  assert.equal(await archivedLinks.first().getAttribute("href"), "/projects/archive12");
  await page.getByRole("searchbox", { name: "Search archived projects", exact: true }).fill("归档最后一个");
  await archive.getByRole("status").getByText("1–1 of 1 projects", { exact: true }).waitFor();
  assert.equal(await archivedLinks.count(), 1);
  assert.equal(await archivedLinks.first().getAttribute("href"), "/projects/archive49");
  assert.equal(await links.count(), 2, "Archive filters do not affect active projects");
  await page.getByLabel("Archived project view", { exact: true }).selectOption("compact");
  await page.setViewportSize({ width: 320, height: 900 });
  await fits();
  assert.deepEqual(errors, []);
  assert.deepEqual(unexpected, []);
  console.log("Browser PASS: 1/2/8/30/200 projects × 6 widths, plus 50 archived; adaptive columns, bounded rendering, all views, whole-library search, publication filter, real-date sorting, paging/reset, no matches, isolated archive tools, no API/provider calls or writes.");
} finally { await browser.close(); }
