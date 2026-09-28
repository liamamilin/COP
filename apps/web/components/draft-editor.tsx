"use client";

import { useMemo, useState } from "react";
import { useRouter } from "next/navigation";

import { ApiError, patchDraftEntity, type DraftEntityKind } from "../lib/api";
import {
  buildPatch,
  changedFields,
  editableFields,
  ENTITY_LABELS,
  type EditableField,
} from "../lib/draft-editing";
import type { COPArtifact } from "@cop-studio/cop-types";

interface DraftEditorProps {
  draftId: string;
  kind: DraftEntityKind;
  entityId: string;
  artifact: COPArtifact;
}

/**
 * Editable form for one entity in the active draft.
 *
 * Saves go through a PATCH that the backend re-validates against the whole
 * artifact, so a rejected edit comes back as an error rather than silently
 * corrupting the draft. The form keeps the user's text on failure: losing a
 * paragraph because one field was rejected is the kind of thing that makes
 * people stop editing.
 */
export function DraftEditor({ draftId, kind, entityId, artifact }: DraftEditorProps) {
  const router = useRouter();
  const initial = useMemo(
    () => editableFields(artifact, kind, entityId),
    [artifact, kind, entityId],
  );
  const [fields, setFields] = useState<EditableField[]>(initial);
  const [pending, setPending] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [saved, setSaved] = useState(false);

  const dirty = changedFields(initial, fields);
  const entityLabel = ENTITY_LABELS[kind];

  function update(name: string, value: string) {
    setSaved(false);
    setFields((current) =>
      current.map((field) => (field.name === name ? { ...field, value } : field)),
    );
  }

  async function save() {
    const patch = buildPatch(initial, fields);
    if (Object.keys(patch).length === 0) {
      setError("Nothing to save.");
      return;
    }
    setPending(true);
    setError(null);
    try {
      await patchDraftEntity(draftId, kind, entityId, patch);
      setSaved(true);
      // The sidebar and draft counts both derive from server data.
      router.refresh();
    } catch (cause) {
      setError(cause instanceof ApiError ? cause.message : "The edit could not be saved.");
    } finally {
      setPending(false);
    }
  }

  function reset() {
    setFields(initial);
    setError(null);
    setSaved(false);
  }

  if (initial.length === 0) {
    return (
      <p className="form-error" role="alert">
        This {entityLabel.toLowerCase()} is not part of the draft.
      </p>
    );
  }

  return (
    <form
      className="draft-editor"
      onSubmit={(event) => {
        event.preventDefault();
        void save();
      }}
    >
      {fields.map((field) => (
        <label className="draft-field" key={field.name}>
          <span>
            {field.label}
            {field.required ? <em>required</em> : null}
          </span>
          {field.multiline ? (
            <textarea
              onChange={(event) => update(field.name, event.target.value)}
              rows={field.name === "definition" ? 4 : 3}
              value={field.value}
            />
          ) : (
            <input
              onChange={(event) => update(field.name, event.target.value)}
              type="text"
              value={field.value}
            />
          )}
        </label>
      ))}

      {error && (
        <p className="form-error" role="alert">
          {error}
        </p>
      )}
      {saved && !error && (
        <p className="draft-saved" role="status">
          Saved to the draft. The published version is unchanged.
        </p>
      )}

      <div className="draft-actions">
        <button className="primary-button" disabled={pending || dirty.length === 0} type="submit">
          {pending ? "Saving…" : "Save to draft"}
        </button>
        <button
          className="secondary-button"
          disabled={pending || dirty.length === 0}
          onClick={reset}
          type="button"
        >
          Reset
        </button>
        {dirty.length > 0 && (
          <span className="draft-dirty">
            {dirty.length} unsaved change{dirty.length === 1 ? "" : "s"}
          </span>
        )}
      </div>
    </form>
  );
}
