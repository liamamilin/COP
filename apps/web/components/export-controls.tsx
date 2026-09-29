"use client";

import { useState } from "react";

import { ApiError, exportVersion, type ExportFormat } from "../lib/api";

export function ExportControls({ versionId }: { versionId: string }) {
  const [pending, setPending] = useState<ExportFormat | null>(null);
  const [error, setError] = useState<string | null>(null);

  async function download(format: ExportFormat) {
    setPending(format);
    setError(null);
    try {
      const result = await exportVersion(versionId, format);
      const url = URL.createObjectURL(result.blob);
      const link = document.createElement("a");
      link.href = url;
      link.download = result.filename;
      document.body.append(link);
      link.click();
      link.remove();
      URL.revokeObjectURL(url);
    } catch (cause) {
      setError(cause instanceof ApiError ? cause.message : "The export could not be created.");
    } finally {
      setPending(null);
    }
  }

  return (
    <div className="export-controls" aria-label="Export published version">
      <button disabled={pending !== null} onClick={() => void download("json")} type="button">
        JSON
      </button>
      <button disabled={pending !== null} onClick={() => void download("markdown")} type="button">
        Markdown
      </button>
      <button
        disabled={pending !== null}
        onClick={() => void download("markdown_bundle")}
        type="button"
      >
        Markdown bundle
      </button>
      {pending && <span role="status">Preparing {pending.replace("_", " ")}…</span>}
      {error && <span className="form-error" role="alert">{error}</span>}
    </div>
  );
}
