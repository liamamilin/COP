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

async function waitForRun(runId: string): Promise<{ status: string }> {
  const deadline = Date.now() + 60_000;
  while (Date.now() < deadline) {
    const response = await fetch(`${API_URL}/generation-runs/${runId}`);
    const run = (await response.json()) as { status: string; error_message?: string };
    if (TERMINAL.has(run.status)) {
      if (!new Set(["completed", "needs_attention"]).has(run.status)) {
        throw new Error(`generation ${run.status}: ${run.error_message ?? "unknown error"}`);
      }
      return run;
    }
    await new Promise((resolve) => setTimeout(resolve, 400));
  }
  throw new Error("generation did not finish");
}

async function downloadText(download: Download): Promise<string> {
  const stream = await download.createReadStream();
  const chunks: Buffer[] = [];
  for await (const chunk of stream) chunks.push(Buffer.from(chunk));
  return Buffer.concat(chunks).toString("utf8");
}

test("the frozen V1 loop reaches a portable Markdown export", async ({ page }) => {
  const project = await post<{ id: string }>("/projects", {
    title: `Frozen V1 ${Date.now()}`,
    domain: "Reliable local knowledge work",
    scope: "Complete the production-to-learning loop",
  });

  try {
    const source = await post<{ id: string; status: string }>(
      `/projects/${project.id}/sources/text`,
      {
        title: "Source brief",
        text: "A COP starts with goals, keeps the main process visible, and makes publishing explicit.",
        format: "text",
      },
    );
    expect(source.status).toBe("ready");

    const run = await post<{ id: string }>(`/projects/${project.id}/generation-runs`, {
      topic: "Reliable local knowledge work",
      mode: "fast",
      source_ids: [source.id],
    });
    await waitForRun(run.id);
    const draft = await post<{ id: string }>(`/projects/${project.id}/drafts/from-run/${run.id}`);
    await post(`/drafts/${draft.id}/publish`, { change_summary: "Frozen V1 acceptance" });

    await page.goto(`/projects/${project.id}`);
    await page.getByRole("link", { name: /Learn/ }).click();
    await expect(page).toHaveURL(`/projects/${project.id}/learn`);
    await waitForHydration(page, ".learn-view");
    const firstStage = page.locator(".learn-stage").first();
    await firstStage.locator(".learn-stage-toggle").focus();
    await page.keyboard.press("Enter");
    await expect(firstStage).toHaveClass(/completed/);

    await page.getByRole("link", { name: /Version history/ }).click();
    await expect(page).toHaveURL(`/projects/${project.id}/versions`);
    await waitForHydration(page, ".export-controls");
    const markdown = page.getByRole("button", { name: "Markdown", exact: true });
    await markdown.focus();
    const [download] = await Promise.all([
      page.waitForEvent("download"),
      page.keyboard.press("Enter"),
    ]);

    expect(download.suggestedFilename()).toMatch(/-v1\.md$/);
    const content = await downloadText(download);
    expect(content).toContain("# Reliable local knowledge work");
    expect(content).toContain("## Goals and main processes");
  } finally {
    await fetch(`${API_URL}/projects/${project.id}`, { method: "DELETE" }).catch(() => undefined);
  }
});

test("appearance settings apply and the mock connection button is live", async ({ page }) => {
  const original = await fetch(`${API_URL}/settings`).then((response) => response.json());
  try {
    await fetch(`${API_URL}/settings`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        provider: { type: "mock", mock_scenario: "success" },
        appearance: { theme: "dark", density: "compact" },
      }),
    });

    await page.goto("/settings");
    await waitForHydration(page, ".settings-form");
    await expect(page.locator("html")).toHaveAttribute("data-theme", "dark");
    await expect(page.locator("html")).toHaveAttribute("data-density", "compact");

    await page.getByRole("button", { name: /Test saved connection/i }).click();
    await expect(page.getByRole("status")).toContainText("connection succeeded");

    await page.locator('select[name="theme"]').selectOption("light");
    await page.locator('select[name="density"]').selectOption("comfortable");
    await page.getByRole("button", { name: /Save settings/i }).click();
    await expect(page.locator("html")).toHaveAttribute("data-theme", "light");
    await expect(page.locator("html")).toHaveAttribute("data-density", "comfortable");
  } finally {
    await fetch(`${API_URL}/settings`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        provider: {
          type: original.provider.type,
          base_url: original.provider.base_url,
          model: original.provider.model,
          timeout: original.provider.timeout,
          max_retries: original.provider.max_retries,
          mock_scenario: original.provider.mock_scenario,
        },
        generation: original.generation,
        appearance: original.appearance,
      }),
    });
  }
});
