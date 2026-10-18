"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";

import { publicApiBaseUrl } from "../lib/api";

/**
 * Duplicate this project.
 *
 * The copy is independent: its own sources, versions, and learning progress. The
 * button says so before it acts, because "duplicate" next to a list of projects
 * can reasonably be read as a link rather than an action.
 */
export function DuplicateButton({ projectId }: { projectId: string }) {
  const router = useRouter();
  const [pending, setPending] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function duplicate() {
    if (
      !window.confirm(
        "Duplicate this project?\n\nThe copy is independent: it gets its own sources and a copy of the latest published version. Your learning progress is not copied.",
      )
    ) {
      return;
    }
    setPending(true);
    setError(null);
    const response = await fetch(`${publicApiBaseUrl()}/projects/${projectId}/duplicate`, {
      method: "POST",
    });
    setPending(false);
    if (response.ok) {
      router.push("/");
      router.refresh();
    } else {
      setError("Unable to duplicate this project.");
    }
  }

  return (
    <>
      <button className="secondary-button" disabled={pending} onClick={duplicate} type="button">
        {pending ? "Duplicating…" : "Duplicate"}
      </button>
      {error && (
        <p className="form-error" role="alert">
          {error}
        </p>
      )}
    </>
  );
}
