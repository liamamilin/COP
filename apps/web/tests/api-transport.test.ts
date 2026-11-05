import { afterEach, expect, it, vi } from "vitest";

import { discardDraft, listGenerationRuns } from "../lib/api";

afterEach(() => {
  vi.unstubAllEnvs();
  vi.unstubAllGlobals();
});

it("discards through the public proxy when only the server's internal URL is configured", async () => {
  vi.stubEnv("INTERNAL_API_BASE_URL", "http://127.0.0.1:18010/api/v1");
  vi.stubEnv("NEXT_PUBLIC_API_BASE_URL", undefined);
  const fetchMock = vi.fn().mockResolvedValue(new Response(null, { status: 204 }));
  vi.stubGlobal("fetch", fetchMock);

  await expect(discardDraft("draft-1")).resolves.toBeUndefined();
  expect(fetchMock).toHaveBeenCalledWith("/api/v1/drafts/draft-1", { method: "DELETE" });
});

it("loads browser history through the public proxy without a build-time public URL", async () => {
  vi.stubGlobal("window", {});
  vi.stubEnv("INTERNAL_API_BASE_URL", "http://127.0.0.1:18010/api/v1");
  vi.stubEnv("NEXT_PUBLIC_API_BASE_URL", undefined);
  const fetchMock = vi.fn().mockResolvedValue(Response.json([]));
  vi.stubGlobal("fetch", fetchMock);

  await expect(listGenerationRuns("project-1")).resolves.toEqual([]);
  expect(fetchMock).toHaveBeenCalledWith("/api/v1/projects/project-1/generation-runs", {
    cache: "no-store",
  });
});
