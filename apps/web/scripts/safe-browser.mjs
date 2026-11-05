/**
 * A guarded Playwright launcher for every local and CI browser check.
 *
 * Why this exists
 * ---------------
 * `@playwright/test@1.64.1` pins Chromium 156.0.8078.4, which predates the
 * 156.0.8078.73 fix for CVE-2026-118306/118331/118344/118348 (arbitrary code
 * execution from a crafted HTML page). Playwright also leaves the Chromium
 * sandbox off by default (`chromiumSandbox` -> `false`), so a compromised
 * renderer is not contained.
 *
 * Instead of removing browser verification entirely, this module refuses the
 * bundled engine and requires a locally installed branded Chrome, with the
 * sandbox explicitly on. That keeps the regression suite meaningful while
 * removing the vulnerable binary from the trust path.
 *
 * What this does NOT do: it cannot make an old system Chrome safe. It only
 * guarantees we never silently fall back to Playwright's pinned build.
 */
import assert from "node:assert/strict";
import { chromium } from "@playwright/test";

/** Chromium build first patched for the four 2026-11 critical CVEs. */
export const MIN_SAFE_CHROMIUM = "156.0.8078.73";

export async function launchChrome() {
  const channel = process.env.PLAYWRIGHT_CHANNEL || "chrome";
  assert.notEqual(
    channel,
    "chromium",
    "Refusing Playwright's bundled Chromium: 1.64.1 ships 156.0.8078.4, which is "
      + `below the ${MIN_SAFE_CHROMIUM} fix boundary. Use an installed Chrome.`,
  );

  const browser = await chromium.launch({
    channel,
    // Playwright defaults this to false. Set it explicitly rather than relying
    // on the default, and pass no `--no-sandbox`-style flags: a stray flag can
    // re-disable the sandbox that this option just turned on.
    chromiumSandbox: true,
  });

  const version = browser.version();
  assert.ok(
    version === "unknown" || compareVersions(version, MIN_SAFE_CHROMIUM) >= 0,
    `Chrome ${version} is older than ${MIN_SAFE_CHROMIUM}; update the browser `
      + "before running browser checks.",
  );
  return browser;
}

/** Numeric dotted-version comparison; avoids a semver dependency. */
export function compareVersions(a, b) {
  const pa = String(a).split(".").map((part) => Number.parseInt(part, 10) || 0);
  const pb = String(b).split(".").map((part) => Number.parseInt(part, 10) || 0);
  for (let index = 0; index < Math.max(pa.length, pb.length); index += 1) {
    const diff = (pa[index] ?? 0) - (pb[index] ?? 0);
    if (diff !== 0) return diff;
  }
  return 0;
}
