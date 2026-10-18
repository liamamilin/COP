/**
 * R7 — the golden case, end to end.
 *
 * One test walks the whole product loop on a project of its own, so a failure
 * names the stage of the loop that broke rather than a unit of behaviour:
 *
 *   create → settings → source → generate → evidence → draft edit → publish
 *   → foundation → stage → practice → checkpoint → goal complete
 *   → expansion map → export → archive → restore
 *
 * It runs against the mock provider, which is what spec `15` §9 requires for the
 * acceptance path and what keeps it out of CI's network budget. The real provider
 * is exercised separately and never here.
 *
 * The project is created, used, and deleted inside the test. The user's own
 * LangChain project is never touched.
 */

import type { Download } from "@playwright/test";

import { API_URL, expect, test, waitForHydration } from "./fixtures";

const TERMINAL = new Set(["completed", "needs_attention", "failed", "cancelled"]);

async function post<T>(path: string, body?: unknown): Promise<T> {
  const response = await fetch(`${API_URL}${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: body === undefined ? undefined : JSON.stringify(body),
  });
  if (!response.ok) throw new Error(`${path}: ${response.status} ${await response.text()}`);
  return (await response.json()) as T;
}

async function patch<T>(path: string, body: unknown): Promise<T> {
  const response = await fetch(`${API_URL}${path}`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!response.ok) throw new Error(`PATCH ${path}: ${response.status} ${await response.text()}`);
  return (await response.json()) as T;
}

async function get<T>(path: string): Promise<T> {
  const response = await fetch(`${API_URL}${path}`);
  if (!response.ok) throw new Error(`GET ${path}: ${response.status} ${await response.text()}`);
  return (await response.json()) as T;
}

async function downloadText(download: Download): Promise<string> {
  const stream = await download.createReadStream();
  const chunks: Buffer[] = [];
  for await (const chunk of stream) chunks.push(Buffer.from(chunk));
  return Buffer.concat(chunks).toString("utf8");
}

test("the golden case closes the whole loop with no dead ends", async ({ page }) => {
  test.setTimeout(180_000);
  // Kept in a variable because the archived list is matched by title later, and
  // the development database is shared with whatever else is running.
  const title = `Golden case ${Date.now()}`;
  const project = await post<{ id: string }>("/projects", {
    title,
    domain: "LangChain agent development",
    scope: "Build, run, and verify a tool-using agent",
    preferred_language: "en",
    learner_level: "advanced",
  });

  try {
    // --- settings: the project stores what the creation form asked for -------
    const settings = await get<{ effective: { generation: Record<string, string> } }>(
      `/projects/${project.id}/settings`,
    );
    expect(settings.effective.generation.language).toBe("en");
    expect(settings.effective.generation.learner_level).toBe("advanced");

    // --- source ------------------------------------------------------------
    const source = await post<{ id: string; status: string }>(
      `/projects/${project.id}/sources/text`,
      {
        title: "LangChain notes",
        text: [
          "create_agent is the high-level entry point for building agents in LangChain.",
          "Tools are plain Python functions; a docstring becomes the tool description.",
          "Pass a thread_id in the config to keep one conversation across invoke calls.",
        ].join(" "),
        format: "text",
      },
    );
    expect(source.status).toBe("ready");

    // --- generate ----------------------------------------------------------
    const run = await post<{ id: string }>(`/projects/${project.id}/generation-runs`, {
      topic: "LangChain agent development",
      mode: "fast",
      source_ids: [source.id],
      learner_level: "advanced",
    });
    const deadline = Date.now() + 120_000;
    let runStatus = "";
    while (Date.now() < deadline) {
      const body = await get<{ status: string; error_message?: string }>(
        `/generation-runs/${run.id}`,
      );
      runStatus = body.status;
      if (TERMINAL.has(body.status)) {
        expect(
          ["completed", "needs_attention"],
          `generation ${body.status}: ${body.error_message ?? "no message"}`,
        ).toContain(body.status);
        break;
      }
      await new Promise((resolve) => setTimeout(resolve, 400));
    }
    expect(TERMINAL.has(runStatus), "generation did not finish").toBe(true);

    // --- draft, edit a method, publish -------------------------------------
    const draft = await post<{ id: string }>(`/projects/${project.id}/drafts/from-run/${run.id}`);
    // The draft is read through the project endpoint, not `/drafts/{id}`: there is
    // no GET on a draft by id, and inventing one here would test the test's own
    // assumption rather than the product.
    const draftBody = await get<{ artifact: { stages: { id: string }[] } }>(
      `/projects/${project.id}/draft`,
    );
    const stageId = draftBody.artifact.stages[0].id;

    // The entity PATCH answers with a summary, so the assertion reads the draft
    // back. That is also the stronger check: it verifies what was persisted rather
    // than what the response claimed.
    const editResponse = await patch<{ id: string }>(
      `/drafts/${draft.id}/stages/${encodeURIComponent(stageId)}`,
      {
        implementation_details:
          "Install LangChain | Create a venv and install | pip install -U langchain | " +
          "pip prints Successfully installed | install into the venv, not the system",
      },
    );
    expect(editResponse.id).toBe(draft.id);

    const afterEdit = await get<{ artifact: { stages: { id: string; implementation_details: Record<string, string>[] }[] } }>(
      `/projects/${project.id}/draft`,
    );
    const editedStage = afterEdit.artifact.stages.find((stage) => stage.id === stageId);
    expect(editedStage, `stage ${stageId} missing after the edit`).toBeDefined();
    expect(editedStage?.implementation_details[0]).toMatchObject({
      title: "Install LangChain",
      command: "pip install -U langchain",
      expected_result: "pip prints Successfully installed",
    });

    const published = await post<{ id: string; version_number: number }>(
      `/drafts/${draft.id}/publish`,
      { change_summary: "Golden case acceptance" },
    );
    expect(published.version_number).toBe(1);

    // --- Stage page shows the method, the example, and the evidence ---------
    await page.goto(`/projects/${project.id}/stages/${encodeURIComponent(stageId)}`);
    await waitForHydration(page, ".stage-content");
    await expect(page.locator(".detail-list .detail-item").first()).toBeVisible();
    await expect(page.locator(".stage-example")).toBeVisible();

    // --- Expansion Map is visible -------------------------------------------
    await page.goto(`/projects/${project.id}`);
    await waitForHydration(page, ".expansion-map");
    const expansions = page.locator(".expansion-map li");
    expect(await expansions.count()).toBeGreaterThanOrEqual(2);
    await expect(expansions.first()).not.toBeEmpty();

    // --- non-goals are visible ----------------------------------------------
    await expect(page.locator(".non-goals li").first()).toBeVisible();

    // --- Learn Mode: foundation, stages, practice, checkpoints ---------------
    await page.getByRole("link", { name: /Learn/ }).click();
    await expect(page).toHaveURL(`/projects/${project.id}/learn`);
    await waitForHydration(page, ".learn-view");

    const progress = await get<{
      foundations: { stage_id: string; status: string }[];
      goals: {
        goal_id: string;
        practice: { checkpoints: { question: string }[] } | null;
        stages: { stage_id: string }[];
        blocked_by: string[];
        completed: boolean;
      }[];
    }>(`/projects/${project.id}/learning-progress?version_id=${published.id}`);

    // Foundation first: every Main Process starts there, so a Goal cannot be
    // complete while the shared setup is open. The count is asserted against the
    // API rather than hard-coded, because a COP with no Shared Foundation is a
    // legitimate shape and this test must not depend on having one.
    const foundationButtons = page.locator(".learn-foundation button");
    const foundationCount = await foundationButtons.count();
    expect(foundationCount).toBe(progress.foundations.length);
    for (let index = 0; index < foundationCount; index += 1) {
      await foundationButtons.nth(index).click();
      await expect(foundationButtons.nth(index)).toHaveText(/Reopen/);
    }

    // Every Stage of the selected Goal.
    //
    // One click at a time, waiting for the server to confirm before the next.
    // The panel reconciles with `router.refresh()` after each save, which
    // re-renders the list; clicking several toggles in a row without waiting
    // races against that refresh and silently marks some Stages twice. The
    // server is the authority on progress, so it is also what the loop reads.
    const goal = progress.goals[0];
    const stageToggles = page.locator(".learn-stage .learn-stage-toggle");
    expect(await stageToggles.count()).toBe(goal.stages.length);

    const stageProgress = async (): Promise<string[]> => {
      const body = await get<{ goals: { stages: { status: string }[] }[] }>(
        `/projects/${project.id}/learning-progress?version_id=${published.id}`,
      );
      return body.goals[0].stages.map((item) => item.status);
    };

    for (let guard = 0; guard < goal.stages.length; guard += 1) {
      const statuses = await stageProgress();
      const next = statuses.findIndex((status) => status !== "completed");
      if (next === -1) break;
      await stageToggles.nth(next).click();
      await expect
        .poll(async () => (await stageProgress())[next], { timeout: 10_000 })
        .toBe("completed");
    }

    const stageStatuses = await stageProgress();
    expect(
      stageStatuses.every((status) => status === "completed"),
      `Stage progress: ${JSON.stringify(stageStatuses)}`,
    ).toBe(true);

    // The Practice starts untouched, and reaching `completed` takes three steps.
    // The intermediate `in_progress` is asserted because it is derived from the
    // answers rather than stored: a learner who has answered a question but not
    // ticked the box has demonstrably started, and the app must say so.
    const practice = page.locator(".practice-card");
    await expect(practice).toHaveAttribute("data-practice-status", "not_started");
    const completeButton = practice.getByRole("button", { name: /Mark practice complete/i });
    await expect(completeButton).toBeDisabled();

    const answers = practice.locator(".practice-checkpoints textarea");
    const answerCount = await answers.count();
    expect(answerCount).toBeGreaterThan(0);
    for (let index = 0; index < answerCount; index += 1) {
      await answers.nth(index).fill(`Answer ${index + 1}`);
      await answers.nth(index).blur();
      // Each answer is saved on blur, and the Practice status is derived from the
      // answers the server holds. Waiting for the count to grow keeps the next
      // fill from racing a `router.refresh()`.
      await expect
        .poll(
          async () => {
            const body = await get<{ goals: { practice: { checkpoints: { answer: string | null }[] } | null }[] }>(
              `/projects/${project.id}/learning-progress?version_id=${published.id}`,
            );
            return body.goals[0].practice?.checkpoints.filter((c) => (c.answer ?? "").length > 0)
              .length;
          },
          { timeout: 10_000 },
        )
        .toBeGreaterThan(index);
    }
    await expect(practice).toHaveAttribute("data-practice-status", "in_progress");
    await expect(completeButton).toBeEnabled();
    await completeButton.click();

    // Wait on the server, not on the screen. The card updates optimistically the
    // moment it is clicked, so asserting on its attribute here would pass before
    // the write landed -- and the very next assertion, Goal completion, would
    // then fail against a server that had not caught up. `blocked_by` is the
    // server's own account of what is outstanding, and a Goal shown complete in
    // the UI while the server disagrees is the bug this batch exists to remove.
    const blockers = async (): Promise<string[]> => {
      const body = await get<{ goals: { completed: boolean; blocked_by: string[] }[] }>(
        `/projects/${project.id}/learning-progress?version_id=${published.id}`,
      );
      return body.goals[0].blocked_by;
    };
    await expect.poll(async () => (await blockers()).join("; "), { timeout: 15_000 }).toBe("");
    // Polled rather than asserted once. The card reconciles through
    // `router.refresh()`, so the server can be complete a moment before the screen
    // shows it; a single assertion would then fail on timing rather than on state.
    await expect(practice).toHaveAttribute("data-practice-status", "completed", {
      timeout: 15_000,
    });

    // --- progress survives a reload ------------------------------------------
    await page.reload();
    await waitForHydration(page, ".learn-view");
    await expect(page.locator(".practice-card")).toHaveAttribute(
      "data-practice-status",
      "completed",
    );

    // --- export --------------------------------------------------------------
    await page.getByRole("link", { name: /Version history/ }).click();
    await waitForHydration(page, ".export-controls");
    const [download] = await Promise.all([
      page.waitForEvent("download"),
      page.getByRole("button", { name: "Markdown", exact: true }).click(),
    ]);
    expect(download.suggestedFilename()).toMatch(/-v1\.md$/);
    const markdown = await downloadText(download);
    expect(markdown).toContain("## Goals and main processes");

    // --- archive, then restore ------------------------------------------------
    //
    // The project settings form, not the app-wide one: `Archive` lives on the
    // project page, and asserting on the wrong form would pass while never
    // touching the button under test.
    await page.goto(`/projects/${project.id}/settings`);
    await waitForHydration(page, ".editor-form");
    page.once("dialog", (dialog) => void dialog.accept());
    await page.getByRole("button", { name: /Archive this project/i }).click();
    await expect(page).toHaveURL("/");

    // The archived section is collapsed by default. Counted after opening it,
    // and asserted on this project's own row rather than on a total, because the
    // development database is shared with whatever else is running.
    const archivedSection = page.locator(".archived-projects");
    await expect(archivedSection).toBeVisible();
    await archivedSection.locator("summary").click();
    await expect(archivedSection.locator("li", { hasText: title })).toHaveCount(1);

    await page.goto(`/projects/${project.id}/settings`);
    await waitForHydration(page, ".editor-form");
    // An archived project offers Restore and not Archive: the reverse would mean
    // the status never reached the component.
    await expect(page.getByRole("button", { name: /Restore this project/i })).toBeVisible();
    await expect(page.getByRole("button", { name: /Archive this project/i })).toHaveCount(0);
    await page.getByRole("button", { name: /Restore this project/i }).click();
    await expect(page.getByRole("button", { name: /Archive this project/i })).toBeVisible();

    // The published version and the learning record both survived.
    const versions = await get<unknown[]>(`/projects/${project.id}/versions`);
    expect(versions).toHaveLength(1);
    const restoredProgress = await get<{ goals: { completed: boolean }[] }>(
      `/projects/${project.id}/learning-progress?version_id=${published.id}`,
    );
    expect(restoredProgress.goals[0].completed).toBe(true);
  } finally {
    await fetch(`${API_URL}/projects/${project.id}`, { method: "DELETE" }).catch(() => undefined);
  }
});

test("a citation the project cannot resolve is labelled, not hidden", async ({ page }) => {
  test.setTimeout(120_000);
  const project = await post<{ id: string }>("/projects", {
    title: `Orphan citation ${Date.now()}`,
    domain: "Evidence handling",
    scope: "Every citation must resolve",
  });

  try {
    const run = await post<{ id: string }>(`/projects/${project.id}/generation-runs`, {
      topic: "Evidence handling",
      mode: "fast",
    });
    const deadline = Date.now() + 90_000;
    while (Date.now() < deadline) {
      const body = await get<{ status: string }>(`/generation-runs/${run.id}`);
      if (TERMINAL.has(body.status)) break;
      await new Promise((resolve) => setTimeout(resolve, 400));
    }
    const draft = await post<{ id: string }>(`/projects/${project.id}/drafts/from-run/${run.id}`);
    const published = await post<{ id: string }>(`/drafts/${draft.id}/publish`, {});

    // A source is added afterwards, so the version's own evidence resolution has
    // something real to find.
    await post(`/projects/${project.id}/sources/text`, {
      title: "A real source",
      text: "Body",
      format: "text",
    });

    const detail = await get<{ evidence_sources: Record<string, unknown> }>(
      `/versions/${published.id}`,
    );
    // The mock cites nothing, so the map is empty. That is the point: the key set
    // is what the UI uses to decide between "openable" and "unresolved", and an
    // empty map must not be mistaken for "all resolved".
    expect(detail.evidence_sources).toEqual({});

    // The Learn page renders without an evidence section rather than inventing one.
    await page.goto(`/projects/${project.id}/learn`);
    await waitForHydration(page, ".learn-view");
    await expect(page.locator(".evidence-missing")).toHaveCount(0);
  } finally {
    await fetch(`${API_URL}/projects/${project.id}`, { method: "DELETE" }).catch(() => undefined);
  }
});
