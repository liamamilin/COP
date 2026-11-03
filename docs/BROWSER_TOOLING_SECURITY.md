# Browser tooling security boundary

Date: 2026-11-03.

## What changed and why

`@playwright/test@1.64.1` bundles Chromium **156.0.8078.4**. Four Chromium
advisories published 2026-10-27 are fixed only in **156.0.8078.73**:

| CVE | Area | Severity |
|---|---|---|
| CVE-2026-118306 | FileSystem memory corruption (escape outside sandbox) | Critical |
| CVE-2026-118331 | FileAPI input validation | High |
| CVE-2026-118344 | Layout use-after-free | Critical |
| CVE-2026-118348 | Skia input validation | High |

Separately, Playwright's `chromiumSandbox` option **defaults to `false`**, so a
compromised renderer is not contained even on an up-to-date build.

Verified locally, not assumed:

- `playwright-core/browsers.json` in 1.64.1 pins `156.0.8078.4`.
- The type definition states `chromiumSandbox?: boolean` → `Defaults to false`.
- The machine's system Chrome is `156.0.8078.80`, above the fix boundary.
- `~/Library/Caches/ms-playwright` did not exist: the bundled browser had never
  been downloaded here. Prior browser runs used `PLAYWRIGHT_CHANNEL=chrome`.

`pnpm install` does **not** download browsers; only `playwright install` does.

## The boundary now enforced

1. **No bundled Chromium.** `apps/web/scripts/safe-browser.mjs` refuses to launch
   when the channel is `chromium`, and every browser script goes through
   `launchChrome()`.
2. **Sandbox on.** `chromiumSandbox: true` is set explicitly in both
   `safe-browser.mjs` and `playwright.config.ts`. No `--no-sandbox`-style flags
   are passed, because a stray flag can undo the option.
3. **Version floor.** `launchChrome()` compares the running major version against
   `156.0.8078.73` and fails the check if the browser is older, instead of
   silently testing on a vulnerable engine.
4. **CI does not install the pinned browser.** The e2e job requires a runner
   Chrome and fails loudly if none exists.

## Architecture impact: none on product code

The change is confined to `apps/web/scripts/`, `apps/web/playwright.config.ts`,
`apps/web/package.json`, `pnpm-lock.yaml`, and the CI e2e job.

- No file under `apps/web/app`, `apps/web/components`, `apps/web/lib`,
  `packages/`, or `backend/app` imports Playwright.
- The backend has no reference to it.
- Product types, schemas, and published artifacts are untouched.

The dependency direction stays one-way: tests depend on the app, never the
reverse. Adding a guard inside the test layer is therefore a leaf change, not an
architectural one.

## What this does not claim

- It does not make an outdated system Chrome safe. The version guard fails the
  run; it cannot patch the browser.
- It does not audit the rest of the dependency tree. The registry mirror in use
  has no audit endpoint, so `pnpm audit` is unavailable here.
- Chromium severity ratings come from Google's advisory text via NVD, not from an
  independent assessment.

## Reproducing the checks

```bash
# Version comparison and bundled-engine refusal, no browser needed
cd apps/web
node --input-type=module -e "import('./scripts/safe-browser.mjs').then(m=>console.log(m.compareVersions('156.0.8078.4', m.MIN_SAFE_CHROMIUM)))"

# Full browser regressions (requires a running stack: make up-local)
for s in scripts/check-*.mjs; do node "$s" || echo "FAIL $s"; done
```
