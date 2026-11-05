import { beforeEach, describe, expect, it, vi } from "vitest";

import { ApiError, createDraftFromRun, getDraft, type DraftDetail } from "../lib/api";
import { prepareGenerationDraft } from "../lib/generation-draft";

vi.mock("../lib/api", async (original) => ({
  ...await original<typeof import("../lib/api")>(),
  createDraftFromRun: vi.fn(),
  getDraft: vi.fn(),
}));

function draft(runId = "run-1", projectId = "project-1") {
  return { id: "draft-1", project_id: projectId, source_run_id: runId } as DraftDetail;
}

beforeEach(() => vi.resetAllMocks());

describe("candidate-to-draft handoff", () => {
  it("opens a newly created draft without publishing", async () => {
    vi.mocked(createDraftFromRun).mockResolvedValue(draft());
    expect(await prepareGenerationDraft("project-1", "run-1"))
      .toEqual({ draft: draft(), matchesRun: true });
    expect(createDraftFromRun).toHaveBeenCalledWith("project-1", "run-1");
    expect(getDraft).not.toHaveBeenCalled();
  });

  it("recovers the matching draft after a reload or duplicate completion", async () => {
    vi.mocked(createDraftFromRun).mockRejectedValue(new ApiError(409, "Draft exists"));
    vi.mocked(getDraft).mockResolvedValue(draft());
    expect((await prepareGenerationDraft("project-1", "run-1")).matchesRun).toBe(true);
  });

  it("does not call an older draft the new generation result", async () => {
    vi.mocked(createDraftFromRun).mockRejectedValue(new ApiError(409, "Draft exists"));
    vi.mocked(getDraft).mockResolvedValue(draft("older-run"));
    expect(await prepareGenerationDraft("project-1", "run-1"))
      .toEqual({ draft: draft("older-run"), matchesRun: false });
    expect(createDraftFromRun).toHaveBeenCalledTimes(1);
  });

  it("surfaces a conflict with no readable draft instead of claiming success", async () => {
    vi.mocked(createDraftFromRun).mockRejectedValue(new ApiError(409, "Conflict"));
    vi.mocked(getDraft).mockResolvedValue(null);
    await expect(prepareGenerationDraft("project-1", "run-1")).rejects.toThrow("could not be opened");
  });

  it("does not hide a server or network error behind an existing draft", async () => {
    vi.mocked(createDraftFromRun).mockRejectedValue(new ApiError(500, "Unavailable"));
    await expect(prepareGenerationDraft("project-1", "run-1")).rejects.toThrow("Unavailable");
    expect(getDraft).not.toHaveBeenCalled();
  });

  it("rejects a draft belonging to another project", async () => {
    vi.mocked(createDraftFromRun).mockResolvedValue(draft("run-1", "other-project"));
    await expect(prepareGenerationDraft("project-1", "run-1")).rejects.toThrow("could not be opened");
  });
});
