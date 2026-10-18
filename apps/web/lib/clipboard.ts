export type CopyResult = "copied" | "unavailable" | "failed";

/** A resolved promise means success; an available API alone does not. */
export async function copyText(text: string, clipboard?: Pick<Clipboard, "writeText">): Promise<CopyResult> {
  if (!clipboard) return "unavailable";
  try {
    await clipboard.writeText(text);
    return "copied";
  } catch {
    return "failed";
  }
}
