import { describe, expect, it, vi } from "vitest";

import { copyText } from "../lib/clipboard";

describe("copyText", () => {
  it("copies the complete unmodified file, not only visible core code", async () => {
    const code = 'print("<script>&")\n' + "# a long source file\n".repeat(100);
    const writeText = vi.fn().mockResolvedValue(undefined);
    expect(await copyText(code, { writeText })).toBe("copied");
    expect(writeText).toHaveBeenCalledWith(code);
  });

  it("does not report success merely because writeText exists", async () => {
    const writeText = vi.fn().mockRejectedValue(new Error("Permission denied"));
    expect(await copyText("file", { writeText })).toBe("failed");
  });

  it("reports an unavailable clipboard without throwing or claiming success", async () => {
    expect(await copyText("file")).toBe("unavailable");
  });
});
