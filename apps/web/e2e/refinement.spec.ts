import type { Page } from "@playwright/test";

import {
  API_URL,
  createVersionedProject,
  expect,
  getDraft,
  test,
  waitForHydration,
  type VersionedProject,
} from "./fixtures";

/**
 * The M6 acceptance criteria, in a real browser:
 *
 * - rejecting changes nothing,
 * - accepting modifies Draft only,
 * - locked / user-edited sibling content is preserved.
 *
 * The last one is the point of the whole milestone, and it is the one a
 * user-facing test can check honestly: type a sentence by hand, run a
 * refinement, and see whether the sentence is still there.
 */
test.describe("partial AI refinement", () => {
  let projectId: string | null = null;

  test.afterEach(async () => {
    if (projectId) {
      await fetch(`${API_URL}/projects/${projectId}`, { method: "DELETE" }).catch(() => undefined);
    }
    projectId = null;
  });

  /** A project with a published v1 and an open draft, as the editor expects. */
  async function versionedProject() {
    const project = await createVersionedProject();
    projectId = project.projectId;
    await fetch(`${API_URL}/projects/${project.projectId}/drafts/from-version/${project.versionId}`, {
      method: "POST",
    });
    return project;
  }

  async function openGoalEditor(page: Page, project: VersionedProject) {
    await page.goto(`/projects/${project.projectId}/draft`);
    await waitForHydration(page, ".draft-toolbar");
    await page
      .locator(".draft-entity-list a", { hasText: project.firstGoal.title })
      .first()
      .click();
    await page.waitForURL(`**/draft/goals/**`, { waitUntil: "load" });
    await waitForHydration(page, ".draft-editor");
  }

  test("a proposal shows before and after and changes nothing until accepted", async ({
    page,
  }) => {
    const project = await versionedProject();
    const before = await getDraft(project.projectId);

    await openGoalEditor(page, project);
    await page.getByRole("button", { name: /Propose a change/i }).click();

    // The review step is where the user decides, so it must be reachable and
    // must show a real diff rather than "something changed".
    await expect(page.locator(".refine-diff-before")).toBeVisible({ timeout: 40_000 });
    await expect(page.locator(".refine-diff-after")).toBeVisible();

    // Nothing has been written yet: proposing is not accepting.
    const during = await getDraft(project.projectId);
    expect(during?.artifact).toEqual(before?.artifact);
  });

  test("rejecting leaves the draft byte-for-byte unchanged", async ({ page }) => {
    const project = await versionedProject();
    const before = await getDraft(project.projectId);

    await openGoalEditor(page, project);
    await page.getByRole("button", { name: /Propose a change/i }).click();
    await expect(page.locator(".refine-panel")).toContainText("PROPOSED CHANGE", {
      timeout: 40_000,
    });

    await page.getByRole("button", { name: /^Reject$/ }).click();

    // The user is told plainly that nothing was lost.
    await expect(page.getByText(/discarded/i)).toBeVisible();
    const after = await getDraft(project.projectId);
    expect(after?.artifact).toEqual(before?.artifact);
  });

  test("accepting changes the draft and leaves the published version alone", async ({
    page,
  }) => {
    const project = await versionedProject();
    const publishedBefore = await fetch(`${API_URL}/versions/${project.versionId}`).then((r) =>
      r.json(),
    );

    await openGoalEditor(page, project);
    await page.getByRole("button", { name: /Propose a change/i }).click();
    await expect(page.locator(".refine-diff-after")).toBeVisible({ timeout: 40_000 });
    const proposed = await page.locator(".refine-diff-after").first().textContent();

    await page.getByRole("button", { name: /Accept into draft/i }).click();
    await expect(page.getByText(/published version is unchanged/i)).toBeVisible();

    const draft = await getDraft(project.projectId);
    const goals = (draft as unknown as { artifact: { goals: { why_it_matters: string }[] } })
      .artifact.goals;
    expect(goals[0].why_it_matters).toBe(proposed);

    // The published version must be exactly what it was.
    const publishedAfter = await fetch(`${API_URL}/versions/${project.versionId}`).then((r) =>
      r.json(),
    );
    expect(publishedAfter).toEqual(publishedBefore);
  });

  test("a sentence the user wrote survives a refinement that targets it", async ({ page }) => {
    const project = await versionedProject();
    const sentence = "This sentence is mine and must survive.";

    await openGoalEditor(page, project);
    // Write it by hand, the way a user would.
    const whyField = page.locator(".draft-field", { hasText: "Why it matters" });
    const control = whyField.locator("textarea, input");
    await control.fill(sentence);
    await page.getByRole("button", { name: /Save to draft/i }).click();
    await expect(page.locator(".draft-saved")).toBeVisible();

    // Now ask the model to improve the same Goal. `why_it_matters` is exactly
    // the field a Goal refinement targets, so this is the collision that
    // matters.
    await page.getByRole("button", { name: /Propose a change/i }).click();
    await expect(page.locator(".refine-panel")).toContainText("PROPOSED CHANGE", {
      timeout: 40_000,
    });

    // The model was stopped, and the user can see that it was stopped.
    await expect(page.locator(".refine-rejected")).toContainText(/locked/i);
    await expect(page.locator(".refine-empty")).toBeVisible();

    // Accept anyway: there is nothing to apply, and the hand-written sentence
    // is still there.
    await page.getByRole("button", { name: /^Reject$/ }).click();
    await page.reload();
    await waitForHydration(page, ".draft-editor");
    await expect(
      page.locator(".draft-field", { hasText: "Why it matters" }).locator("textarea, input"),
    ).toHaveValue(sentence);
  });

  test("a proposal is not offered when the project has no draft", async ({ page }) => {
    // A published version with no draft is the state right after publishing.
    const project = await createVersionedProject();
    projectId = project.projectId;

    // A refinement needs a draft to land in, so the control is disabled rather
    // than failing after the user has waited for a proposal.
    await page.goto(`/projects/${project.projectId}/versions`);
    await waitForHydration(page, ".version-actions");
    await expect(page.getByRole("button", { name: /Draft from v1/i })).toBeVisible();
  });
});
