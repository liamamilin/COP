import { defineConfig, devices } from "@playwright/test";
const remote = process.env.ATLAS_TEST_URL;
export default defineConfig({
  testDir: "./e2e",
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 1 : 0,
  workers: process.env.CI ? 2 : 3,
  reporter: [["list"]],
  timeout: 30000,
  use: {
    baseURL: remote || "http://127.0.0.1:4174/COP/",
    trace: "retain-on-failure",
    screenshot: "only-on-failure",
    // Share Studio's system Chrome policy and keep the renderer sandbox enabled.
    channel: "chrome",
    launchOptions: { chromiumSandbox: true },
  },
  webServer: remote
    ? undefined
    : {
        command: "pnpm preview",
        url: "http://127.0.0.1:4174/COP/",
        reuseExistingServer: !process.env.CI,
      },
  projects: [
    { name: "desktop", use: { ...devices["Desktop Chrome"] } },
    {
      name: "mobile",
      use: { ...devices["iPhone 13"], defaultBrowserType: "chromium" },
    },
  ],
});
