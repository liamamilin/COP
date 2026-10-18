"use client";

import { useState } from "react";

import { copyText, type CopyResult } from "../lib/clipboard";

/**
 * Copy some text to the clipboard.
 *
 * A separate client module because the components that use it are server
 * components: an `onClick` inside a server component is the error "Event
 * handlers cannot be passed to Client Component props", which surfaced as the
 * whole Stage page falling back to the error boundary rather than as anything
 * to do with copying.
 *
 * The failure mode of a copy button that silently does nothing is worse than no
 * button, so an unavailable clipboard says so instead of pretending.
 */
export function CopyButton({ text, label = "Copy" }: { text: string; label?: string }) {
  const [result, setResult] = useState<{ text: string; status: CopyResult | "pending" } | null>(null);
  const status = result?.text === text ? result.status : null;
  async function copy() {
    setResult({ text, status: "pending" });
    try {
      setResult({ text, status: await copyText(text, navigator.clipboard) });
    } catch {
      // Some browser policies throw even when reading the clipboard property.
      setResult({ text, status: "failed" });
    }
  }
  return (
    <span className="copy-action">
      <button className="copy-button" disabled={status === "pending"} onClick={() => void copy()} type="button">
        {status === "copied" ? "Copied" : status === "pending" ? "Copying…" : label}
      </button>
      {(status === "failed" || status === "unavailable") && (
        <span role="status">Copy unavailable. Open the code and select it manually.</span>
      )}
    </span>
  );
}
