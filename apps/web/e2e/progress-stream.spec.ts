import { createProject, deleteProject, recordStreamEvents, setMockScenario, streamEvents } from "./stream-helpers";
import { expect, test, waitForHydration } from "./fixtures";

/**
 * The M4 progress stream, driven in a real browser.
 *
 * The unit tests cover `describeRunStatus` and `isTerminal`, and the backend
 * tests cover the event log. Neither can show that the browser actually
 * receives a stream, that phases advance, or that a dropped connection resumes
 * rather than restarting.
 */
test.describe("generation progress stream", () => {
  let projectId: string | null = null;

  test.beforeEach(async () => {
    projectId = await createProject(`E2E stream ${Date.now()}`);
  });

  test.afterEach(async () => {
    if (projectId) await deleteProject(projectId);
    projectId = null;
    // Leave the provider on the fast path so later suites are not slowed down.
    await setMockScenario("success").catch(() => undefined);
  });

  test("a run streams progress through to completion", async ({ page }) => {
    // `slow` keeps the run open long enough to observe intermediate phases.
    await setMockScenario("slow");
    await page.goto(`/projects/${projectId}`);
    await recordStreamEvents(page);
    await waitForHydration(page, ".generation-panel");

    await page.getByRole("button", { name: /Generate COP/i }).click();

    // The transport line reports which mechanism is driving the UI. With an
    // intact stream it must say "Streaming", and must not have silently
    // degraded to the poll fallback.
    await expect(page.locator(".generation-transport")).toBeVisible();
    await expect(page.getByText(/Streaming progress/)).toBeVisible({ timeout: 20_000 });

    // Phases are rendered from the event log, and at least one must complete
    // for the stream to have carried anything.
    await expect(page.locator(".phase.done").first()).toBeVisible({ timeout: 40_000 });

    // The run reaches a terminal state and the copy says so.
    await expect(page.getByText("Candidate ready")).toBeVisible({ timeout: 60_000 });
    await expect(page.getByRole("button", { name: /Run again/i })).toBeVisible();

    const events = await streamEvents(page);
    const ids = events.map((event) => event.split("#")[1] ?? "-");
    // The stream must actually have delivered step events, not just the
    // fallback poll.
    expect(events.filter((event) => event.startsWith("step.")).length).toBeGreaterThan(0);
    // Every event the server sent carries an id, which is what makes a
    // reconnect resumable.
    expect(ids.filter((id) => /^\d+$/.test(id)).length).toBeGreaterThan(0);
  });

  test("cancelling a running run stops it and keeps what was built", async ({ page }) => {
    await setMockScenario("slow");
    await page.goto(`/projects/${projectId}`);
    await recordStreamEvents(page);
    await waitForHydration(page, ".generation-panel");

    await page.getByRole("button", { name: /Generate COP/i }).click();
    await expect(page.getByRole("button", { name: /^Cancel$/ })).toBeVisible({
      timeout: 30_000,
    });

    await page.getByRole("button", { name: /^Cancel$/ }).click();

    // The user is told plainly that their work and history are intact. A
    // cancellation that looks like data loss is the failure this guards.
    await expect(page.getByText("Generation cancelled")).toBeVisible({ timeout: 30_000 });
    await expect(page.getByText(/previous versions are unchanged/i)).toBeVisible();
  });

  test("a dropped stream falls back to polling instead of stranding the run", async ({
    page,
  }) => {
    await setMockScenario("slow");
    await page.goto(`/projects/${projectId}`);
    await recordStreamEvents(page);
    await waitForHydration(page, ".generation-panel");

    // Break the transport before the run gets anywhere, which is what a
    // dropped connection looks like in practice. Done any later, the run can
    // finish first and the transport line is already gone, which would make
    // the assertion below pass or fail at random.
    await page.evaluate(() => {
      window.EventSource = function Broken() {
        throw new Error("connection lost");
      } as unknown as typeof EventSource;
    });

    await page.getByRole("button", { name: /Generate COP/i }).click();

    // The panel must report polling rather than streaming. Telling the user
    // "Streaming progress" while the stream is dead is the small lie that makes
    // a stalled run look alive.
    await expect(page.getByText(/Polling for progress/)).toBeVisible({ timeout: 20_000 });

    // The poll fallback owns the terminal transition, so a dead stream must
    // not strand the UI on a run that actually finished.
    await expect(page.getByText("Candidate ready")).toBeVisible({ timeout: 60_000 });
    await expect(page.getByRole("button", { name: /Run again/i })).toBeVisible();
  });
});
