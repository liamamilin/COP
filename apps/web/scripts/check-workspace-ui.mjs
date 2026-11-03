// Read-only check against an already-running app and a published project.
// Usage: PLAYWRIGHT_CHANNEL=chrome node scripts/check-workspace-ui.mjs PROJECT_URL API_BASE_URL
// Optional SCREENSHOT_DIR saves desktop/mobile overview and Learn screenshots.
import assert from "node:assert/strict";
import { mkdir } from "node:fs/promises";
import { join } from "node:path";
import { chromium } from "@playwright/test";

const [projectUrl, apiBase] = process.argv.slice(2);
assert.ok(projectUrl && apiBase, "Provide a published PROJECT_URL and API_BASE_URL; this check never starts services.");
const url = new URL(projectUrl);
const projectPath = url.pathname.replace(/\/$/, "");
assert.match(projectPath, /^\/projects\/[^/]+$/);
const projectId = decodeURIComponent(projectPath.split("/").at(-1));
const api = apiBase.replace(/\/$/, "");
const screenshots = process.env.SCREENSHOT_DIR;
if (screenshots) await mkdir(screenshots, { recursive: true });

async function read(path) {
  const response = await fetch(`${api}${path}`);
  assert.ok(response.ok, `GET ${path}: ${response.status}`);
  return response.json();
}
const versionPath = `/projects/${encodeURIComponent(projectId)}/versions/latest`;
const beforeVersion = await read(versionPath);
const progressPath = `/projects/${encodeURIComponent(projectId)}/learning-progress?version_id=${encodeURIComponent(beforeVersion.id)}`;
const beforeProgress = await read(progressPath);
const artifact = beforeVersion.artifact;
const project = await read(`/projects/${encodeURIComponent(projectId)}`);
const first = (items) => encodeURIComponent(items[0].id);
const routes = [
  ["overview", projectPath],
  ["goal", `${projectPath}/goals/${first(artifact.goals)}`],
  ["process", `${projectPath}/processes/${first(artifact.main_processes)}`],
  ["stage", `${projectPath}/stages/${first(artifact.stages)}`],
  ...(artifact.concepts.length ? [["concept", `${projectPath}/concepts/${first(artifact.concepts)}`]] : []),
  ...(artifact.operations.length ? [["operation", `${projectPath}/operations/${first(artifact.operations)}`]] : []),
  ["learn", `${projectPath}/learn`],
  ["versions", `${projectPath}/versions`],
  ["sources", `${projectPath}/sources`],
  ["settings", `${projectPath}/settings`],
];
const browser = await chromium.launch({ channel: process.env.PLAYWRIGHT_CHANNEL || undefined });
const writes = [];
const errors = [];
try {
  for (const width of [1440, 1024, 390, 320]) {
    const context = await browser.newContext({ viewport: { width, height: 1000 }, colorScheme: "light" });
    await context.route("**/*", async (route) => {
      const request = route.request();
      if (!["GET", "HEAD"].includes(request.method())) {
        writes.push(`${request.method()} ${request.url()}`);
        return route.abort();
      }
      return route.continue();
    });
    const page = await context.newPage();
    page.on("pageerror", (error) => errors.push(error.message));
    // Hydration mismatches are console errors, not uncaught page exceptions.
    page.on("console", (message) => {
      if (message.type() === "error") errors.push(message.text());
    });
    for (const [name, path] of routes) {
      const response = await page.goto(new URL(path, url).href);
      assert.equal(response?.status(), 200, `${name} should load`);
      await page.locator(".published-workspace h1").waitFor();
      const measured = await page.evaluate(() => ({
        overflow: document.documentElement.scrollWidth - innerWidth,
        titles: [...document.querySelectorAll(".published-workspace h1")].map((el) => parseFloat(getComputedStyle(el).fontSize)),
        leads: [...document.querySelectorAll(".published-workspace .lead-copy, .published-workspace .local-goal-block p")].map((el) => parseFloat(getComputedStyle(el).fontSize)),
      }));
      assert.ok(measured.overflow <= 1, `${name} overflows at ${width}px by ${measured.overflow}px`);
      assert.ok(measured.titles.every((size) => size <= 32), `${name} has display-sized titles at ${width}px`);
      assert.ok(measured.leads.every((size) => size <= 14), `${name} has display-sized prose at ${width}px`);
      if (name === "overview") {
        assert.equal(await page.locator("h1").innerText(), project.title);
        const learn = page.getByRole("link", { name: "Open Learn →", exact: true });
        const box = await learn.boundingBox();
        assert.ok(box && box.y + box.height < 844, `Learn entry should fit the first screen at ${width}px`);
        assert.equal(new URL(await learn.getAttribute("href"), url).searchParams.get("version"), beforeVersion.id);
        assert.ok((await page.locator(".learning-approach").innerText()).includes(artifact.domain.name));
        await page.locator(".workspace-context > summary").click();
        assert.ok((await page.locator(".workspace-context").innerText()).includes(artifact.domain.scope));
        await page.locator(".workspace-context > summary").click();
        await page.evaluate(() => scrollTo(0, 0));
      }
      if (name === "learn") {
        assert.equal(await page.locator(".learn-goal").count(), artifact.goals.length);
        const reader = page.locator(".learn-detail");
        await reader.locator('[data-guide-section="instructions"]').waitFor();
        assert.ok(await reader.locator('[data-guide-section="instructions"]').isVisible());
        assert.equal(await reader.locator('[data-guide-section="background"]').getAttribute("open"), null);
        const secondStep = page.locator(".learn-stage-open").nth(1);
        if (await secondStep.count()) {
          const target = new URL(await secondStep.getAttribute("href"), page.url());
          const versionId = target.searchParams.get("version");
          await secondStep.click();
          await page.waitForURL(target.href);
          await page.locator(".learn-current-stage-title").waitFor();
          assert.equal(new URL(page.url()).searchParams.get("version"), versionId);
          const stageId = target.searchParams.get("stage");
          assert.equal(await page.locator(".learn-current-stage-title").innerText(), artifact.stages.find((s) => s.id === stageId).title);
          await page.goto(new URL(path, url).href);
          await page.locator(".learn-view").waitFor();
        }
        const summary = page.locator(".learn-foundation-content summary").first();
        if (await summary.count()) {
          await summary.click();
          assert.ok(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth + 1), "Open foundation should fit");
          await summary.click();
          await page.evaluate(() => scrollTo(0, 0));
        }
      }
      if (screenshots && [1440, 390].includes(width) && ["overview", "learn"].includes(name)) {
        await page.screenshot({ path: join(screenshots, `cop-${name}-${width}.png`) });
      }
    }
    await context.close();
  }
  assert.deepEqual(writes, [], "No writes, progress updates, publishing or generation are allowed");
  assert.deepEqual(errors, [], "No browser runtime or hydration/console errors");
  assert.deepEqual(await read(versionPath), beforeVersion, "Published artifact must stay unchanged");
  assert.deepEqual(await read(progressPath), beforeProgress, "Learning progress must stay unchanged");
  console.log(`Browser PASS: ${routes.length} published pages × 4 viewport widths, restrained type, no overflow, no writes, unchanged artifact and progress.`);
} finally {
  await browser.close();
}
