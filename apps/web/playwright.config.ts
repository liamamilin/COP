import { defineConfig, devices } from "@playwright/test";

/**
 * E2E runs against the real Compose stack, not a mock.
 *
 * The behaviour worth protecting here cannot be observed in a unit test: it
 * lives in the interaction between the client component, the JSONB draft row,
 * and the validation the API re-runs on every write. A fake fetch would assert
 * only that the fake was called.
 *
 * The suite talks to a throwaway database seeded by `globalSetup`, for the same
 * reason `make test` does: these tests truncate tables, and pointing them at
 * the development database would delete real projects.
 *
 * Start the stack first (`POSTGRES_HOST_PORT=55432 docker compose up -d`), or
 * set E2E_BASE_URL when the app is already listening elsewhere.
 */
const BASE_URL = process.env.E2E_BASE_URL ?? "http://localhost:3000";
const API_URL = process.env.E2E_API_URL ?? "http://localhost:8000/api/v1";

export default defineConfig({
  testDir: "./e2e",
  // Serial: every test shares one seeded project, and a parallel worker would
  // truncate another's fixture mid-assertion.
  workers: 1,
  fullyParallel: false,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 1 : 0,
  reporter: process.env.CI ? [["github"], ["list"]] : [["list"]],
  timeout: 45_000,
  expect: { timeout: 10_000 },
  use: {
    baseURL: BASE_URL,
    trace: "retain-on-failure",
    screenshot: "only-on-failure",
  },
  globalSetup: "./e2e/global-setup.ts",
  projects: [{ name: "chromium", use: { ...devices["Desktop Chrome"] } }],
  metadata: { apiUrl: API_URL },
});
