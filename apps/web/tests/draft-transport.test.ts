import { afterEach, expect, it, vi } from "vitest";

import { discardDraft } from "../lib/api";

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
