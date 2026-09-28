import { getLearningProgress } from "../lib/api";

import {
  API_URL,
  createVersionedProject,
  expect,
  test,
  waitForHydration,
  type VersionedProject,
} from "./fixtures";

/**
 * The M7 acceptance criteria:
 *
 * - reload does not lose progress,
 * - switching artifact version does not corrupt progress records,
 * - the full Main Process stays visible.
 *
 * The last one gets the most attention because it is the product's central
 * claim, and it is the one a progress UI tends to break while adding progress
 * UI: it is very easy to render "the stage you are on" and quietly drop the
 * rest of the main line.
 */
test.describe("learn mode", () => {
  let projectId: string | null = null;

  test.afterEach(async () => {
    if (projectId) {
      await fetch(`${API_URL}/projects/${projectId}`, { method: "DELETE" }).catch(() => undefined);
    }
    projectId = null;
  });

  async function published(): Promise<VersionedProject> {
    const project = await createVersionedProject();
    projectId = project.projectId;
    return project;
  }

  async function openLearn(page: import("@playwright/test").Page, project: VersionedProject) {
    await page.goto(`/projects/${project.projectId}/learn`);
    await waitForHydration(page, ".learn-view");
  }

  test("the whole Main Process is on screen at once", async ({ page }) => {
    const project = await published();
    await openLearn(page, project);

    const stages = await page.locator(".learn-stages .learn-stage").count();
    const total = await getLearningProgress(project.projectId);
    const firstGoal = total.goals[0];

    // Every Stage of the process, not just the current one, plus the start and
    // the outcome. This is the invariant: you can always see the whole line.
    expect(stages).toBe(firstGoal.total_stages);
    expect(stages).toBeGreaterThan(1);
    await expect(page.locator(".learn-stage-zero")).toBeVisible();
    await expect(page.locator(".learn-stage-outcome")).toBeVisible();
    // The process title is on screen, not just its stages.
    await expect(page.locator(".learn-mainline h2")).toBeVisible();
  });

  test("progress survives a reload", async ({ page }) => {
    const project = await published();
    await openLearn(page, project);

    await page.locator(".learn-stages .learn-stage").first().locator(".learn-stage-toggle").click();
    await expect(page.locator(".learn-stages .learn-stage").first()).toHaveClass(/completed/);

    // A full document load, so this proves it came from the database.
    await page.reload();
    await waitForHydration(page, ".learn-view");
    await expect(page.locator(".learn-stages .learn-stage").first()).toHaveClass(/completed/);

    const stored = await getLearningProgress(project.projectId);
    expect(stored.goals[0].completed_stages).toBe(1);
  });

  test("a completed stage can be reopened", async ({ page }) => {
    const project = await published();
    await openLearn(page, project);

    const first = page.locator(".learn-stages .learn-stage").first();
    await first.locator(".learn-stage-toggle").click();
    await expect(first).toHaveClass(/completed/);
    await first.locator(".learn-stage-toggle").click();
    await expect(first).not.toHaveClass(/completed/);

    const stored = await getLearningProgress(project.projectId);
    expect(stored.goals[0].completed_stages).toBe(0);
  });

  test("the current stage detail stays visible while the main line is shown", async ({ page }) => {
    const project = await published();
    await openLearn(page, project);

    // Structure before detail: the process and the stage detail are both on
    // screen, so the user never loses the line of sight.
    await expect(page.locator(".learn-mainline")).toBeVisible();
    await expect(page.locator(".learn-detail-card")).toBeVisible();
    await expect(page.locator(".learn-detail-card h3")).toBeVisible();
  });

  test("switching version shows that version's own progress", async ({ page }) => {
    const project = await published();
    await openLearn(page, project);

    const first = page.locator(".learn-stages .learn-stage").first();
    await first.locator(".learn-stage-toggle").click();
    await expect(first).toHaveClass(/completed/);

    // Publish a second version that reuses the same entity ids, the case where
    // progress could leak across histories.
    const v2 = await fetch(`${API_URL}/projects/${project.projectId}/drafts/from-version/${project.versionId}`, {
      method: "POST",
    });
    const draft = await v2.json();
    await fetch(`${API_URL}/drafts/${draft.id}/publish`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ change_summary: "v2" }),
    });

    // v1's progress is intact...
    const one = await getLearningProgress(project.projectId, project.versionId);
    expect(one.goals[0].completed_stages).toBe(1);
    // ...and v2 starts clean rather than inheriting it.
    const versions = await fetch(`${API_URL}/projects/${project.projectId}/versions`).then((r) =>
      r.json(),
    );
    const latest = versions[0].id;
    const two = await getLearningProgress(project.projectId, latest);
    expect(two.version_id).toBe(latest);
    expect(two.goals[0].completed_stages).toBe(0);
  });

  test("a goal can be chosen from the goal list", async ({ page }) => {
    const project = await published();
    await openLearn(page, project);

    const goals = page.locator(".learn-goal");
    await expect(goals).toHaveCount((await getLearningProgress(project.projectId)).total_goals);

    if ((await goals.count()) > 1) {
      // Assert on which goal is marked active rather than on the process title:
      // two Goals can legitimately share a process title, which would make a
      // text comparison pass or fail for the wrong reason.
      await expect(goals.first()).toHaveClass(/active/);

      // The second Goal's link points at its own URL, and that URL selects it.
      //
      // Navigating by `goto` rather than by clicking is deliberate. Client-side
      // navigation in this build intermittently does not happen at all -- the
      // same root cause behind the `router.push` workaround in
      // start-draft-button.tsx -- while the destination renders correctly every
      // time. Clicking here would make the suite flaky for a reason that has
      // nothing to do with Learn Mode.
      const href = await goals.nth(1).getAttribute("href");
      expect(href).toContain("goal=");
      expect(href).toContain("version=");

      await page.goto(href!);
      await waitForHydration(page, ".learn-view");
      await expect(goals.nth(1)).toHaveClass(/active/);
      await expect(goals.first()).not.toHaveClass(/active/);
    }
  });
});
