// Read-only homepage regression; never starts services or writes project data.
// Usage: PLAYWRIGHT_CHANNEL=chrome node scripts/check-home-library-ui.mjs APP_URL API_BASE_URL
import assert from "node:assert/strict";
import { mkdir } from "node:fs/promises";
import { join } from "node:path";
import { chromium } from "@playwright/test";

const [appUrl, apiBase] = process.argv.slice(2);
assert.ok(appUrl && apiBase, "Provide the running APP_URL and API_BASE_URL.");
const base = new URL(appUrl);
const api = apiBase.replace(/\/$/, "");
async function snapshot() {
  return Promise.all(["/projects", "/projects?status=archived"].map(async (path) => {
    const response = await fetch(`${api}${path}`);
    assert.ok(response.ok);
    return response.json();
  }));
}
const before = await snapshot();
const screenshotDir = process.env.SCREENSHOT_DIR;
if (screenshotDir) await mkdir(screenshotDir, { recursive: true });
const browser = await chromium.launch({ channel: process.env.PLAYWRIGHT_CHANNEL || undefined });
const writes = [];
const errors = [];
try {
  for (const width of [1440, 1024, 390, 320]) {
    for (const scheme of ["light", "dark"]) {
      const context = await browser.newContext({ viewport: { width, height: 900 }, colorScheme: scheme });
      await context.route("**/*", (route) => {
        if (!["GET", "HEAD"].includes(route.request().method())) {
          writes.push(`${route.request().method()} ${route.request().url()}`);
          return route.abort();
        }
        return route.continue();
      });
      const page = await context.newPage();
      page.on("pageerror", (error) => errors.push(error.message));
      page.on("console", (message) => { if (message.type() === "error") errors.push(message.text()); });
      await page.goto(base.href);
      await page.getByRole("heading", { name: "Projects", exact: true }).waitFor();
      const measured = await page.evaluate(() => ({
        overflow: document.documentElement.scrollWidth - innerWidth,
        titleSize: parseFloat(getComputedStyle(document.querySelector("main h1")).fontSize),
      }));
      assert.ok(measured.overflow <= 1, `Library overflow at ${width}px (${scheme})`);
      assert.ok(measured.titleSize <= 32, "No display-sized headline");
      const create = page.getByRole("link", { name: "New project", exact: true });
      assert.equal(await create.getAttribute("href"), "/projects/new");
      assert.ok((await create.boundingBox()).y < 844, "Creation is visible on the first screen");
      const cards = page.getByRole("link", { name: /^Open project:/ });
      assert.equal(await cards.count(), before[0].length);
      if (before[0].length) {
        const first = cards.first();
        const box = await first.boundingBox();
        assert.ok(box.y < 600, "The first project's content starts on the first screen");
        assert.ok(box.height <= 460, "Project previews must not expand into full lesson outlines");
        if (width >= 1024) {
          assert.ok(box.x < 50, "Use the desktop width rather than a narrow centered list");
          if (before[0].length > 1) {
            const second = await cards.nth(1).boundingBox();
            assert.ok(Math.abs(box.y - second.y) < 2, "Desktop projects use balanced side-by-side cards");
          }
        }
        await first.focus();
        assert.equal(await first.evaluate((el) => el === document.activeElement), true);
        assert.ok(await first.locator("h3").evaluate((el) => parseFloat(getComputedStyle(el).fontSize) <= 18));
        await first.evaluate((el) => el.blur());
      }
      if (screenshotDir && [1440, 390].includes(width) && scheme === "light") {
        await page.screenshot({ path: join(screenshotDir, `cop-home-library-${width}.png`) });
      }
      if (before[0].length) {
        const firstCard = cards.first().locator("..");
        assert.equal(await firstCard.getByRole("button", { name: "Delete", exact: true }).count(), 0, "Destructive actions stay out of the default view");
        const actions = firstCard.getByRole("button", { name: /^Actions for / });
        await actions.click();
        await firstCard.getByRole("button", { name: "Delete", exact: true }).click();
        const confirmation = firstCard.getByRole("textbox", { name: "Type the project title to confirm" });
        await confirmation.waitFor();
        assert.ok(await firstCard.getByRole("button", { name: "Confirm delete", exact: true }).isDisabled());
        assert.ok(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth + 1), "Delete confirmation fits without overflow");
        await firstCard.getByRole("button", { name: "Cancel", exact: true }).click();
        assert.equal(await actions.evaluate((el) => el === document.activeElement), true, "Cancel restores focus to the action trigger");
        const href = await cards.first().getAttribute("href");
        await cards.first().press("Enter");
        await page.waitForURL(new URL(href, base).href);
        await page.locator(".workspace-main").waitFor();
        await page.getByRole("link", { name: "All projects", exact: true }).click();
        await page.getByRole("heading", { name: "Projects", exact: true }).waitFor();
      }
      await context.close();
    }
  }
  assert.deepEqual(writes, []);
  assert.deepEqual(errors, [], "No rendering, hydration or console errors");
  assert.deepEqual(await snapshot(), before, "Projects must stay unchanged");
  console.log("Browser PASS: library and safe confirmation, 4 widths × 2 color schemes, keyboard navigation, no console/hydration errors, no writes.");
} finally { await browser.close(); }
