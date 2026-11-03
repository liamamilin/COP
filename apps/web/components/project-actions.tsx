"use client";

import { useEffect, useId, useRef, useState } from "react";

import { ApiError, archiveProject, deleteProject, restoreProject } from "../lib/api";

import styles from "./project-actions.module.css";

type Action = "archive" | "delete" | "restore";

/** Only lifecycle confirmation/persistence. No library, COP, or generation state. */
export function ProjectActions({ projectId, title, archived = false }: {
  projectId: string; title: string; archived?: boolean;
}) {
  const [mode, setMode] = useState<Action | null>(null);
  const [menuOpen, setMenuOpen] = useState(false);
  const [confirmation, setConfirmation] = useState("");
  const [pending, setPending] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const busy = useRef(false);
  const input = useRef<HTMLInputElement>(null);
  const trigger = useRef<HTMLButtonElement | null>(null);
  const menu = useRef<HTMLDivElement>(null);
  const cancelButton = useRef<HTMLButtonElement>(null);
  const id = useId();

  useEffect(() => {
    if (mode === "delete") input.current?.focus();
    else if (mode) cancelButton.current?.focus();
  }, [mode]);

  useEffect(() => {
    if (!menuOpen) return;
    menu.current?.querySelector<HTMLButtonElement>("[data-action-option]")?.focus();
    function dismiss(event: PointerEvent) {
      if (event.target instanceof Node && !menu.current?.contains(event.target)) setMenuOpen(false);
    }
    document.addEventListener("pointerdown", dismiss);
    return () => document.removeEventListener("pointerdown", dismiss);
  }, [menuOpen]);

  function open(action: Action) {
    setMenuOpen(false);
    setMode(action);
    setConfirmation("");
    setError(null);
  }

  function cancel() {
    if (busy.current) return;
    setMode(null);
    setConfirmation("");
    setError(null);
    trigger.current?.focus();
  }

  async function confirm() {
    if (!mode || busy.current || (mode === "delete" && confirmation.trim() !== title.trim())) return;
    busy.current = true;
    setPending(true);
    setError(null);
    try {
      if (mode === "delete") await deleteProject(projectId);
      else if (mode === "archive") await archiveProject(projectId);
      else await restoreProject(projectId);
      // Reload after success so the server-owned active/archive lists cannot
      // retain a stale card. This runs only after an explicit confirmed write.
      window.location.assign("/");
    } catch (cause) {
      setError(cause instanceof ApiError ? cause.message : "The request could not be confirmed. Reload the library before trying again.");
      busy.current = false;
      setPending(false);
    }
  }

  return (
    <div className={styles.actions} data-project-actions={projectId}>
      <div className={styles.menu} ref={menu} onBlur={(event) => {
        if (!event.currentTarget.contains(event.relatedTarget)) setMenuOpen(false);
      }} onKeyDown={(event) => {
        if (event.key === "Escape" && menuOpen) {
          event.preventDefault();
          event.stopPropagation();
          setMenuOpen(false);
          trigger.current?.focus();
        }
      }}>
        <button ref={trigger} className={styles.menuTrigger} type="button" aria-label={`Actions for ${title}`} aria-expanded={menuOpen} aria-controls={menuOpen ? `${id}-options` : undefined} disabled={pending} onClick={() => {
          setMode(null);
          setError(null);
          setConfirmation("");
          setMenuOpen(!menuOpen);
        }}><span aria-hidden="true">⋯</span></button>
        {menuOpen && <div id={`${id}-options`} className={styles.buttons} role="group" aria-label="Project management">
          <button type="button" data-action-option onClick={() => open(archived ? "restore" : "archive")}>{archived ? "Restore" : "Archive"}</button>
          <button className={styles.deleteButton} type="button" data-action-option onClick={() => open("delete")}>Delete</button>
        </div>}
      </div>
      {mode && <div className={styles.confirmation} role="group" aria-labelledby={`${id}-heading`} onKeyDown={(event) => { if (event.key === "Escape") cancel(); }}>
        <h4 id={`${id}-heading`}>{mode === "delete" ? "Delete this project?" : mode === "archive" ? "Archive this project?" : "Restore this project?"}</h4>
        <p className={styles.projectTitle}>{title}</p>
        <p>{mode === "delete"
          ? "It will disappear from both active and archived lists. There is no restore in the app. This does not erase stored files; archive instead if you may need the project again."
          : mode === "archive" ? "Remove it from the active list while keeping its sources, versions and learning records. You can restore it from Archived projects."
          : "Bring this project back to the active list with its existing sources, versions and learning records."}</p>
        {mode === "delete" && <label htmlFor={`${id}-title`}>Type the project title to confirm
          <input ref={input} id={`${id}-title`} value={confirmation} disabled={pending} onChange={(event) => setConfirmation(event.target.value)} autoComplete="off" spellCheck={false} />
        </label>}
        {error && <p className={styles.error} role="alert">{error}</p>}
        <div className={styles.confirmButtons}>
          <button ref={cancelButton} type="button" disabled={pending} onClick={cancel}>Cancel</button>
          <button className={mode === "delete" ? styles.confirmDelete : styles.confirm} type="button" disabled={pending || (mode === "delete" && confirmation.trim() !== title.trim())} onClick={() => void confirm()}>
            {pending ? "Working…" : mode === "delete" ? "Confirm delete" : mode === "archive" ? "Confirm archive" : "Confirm restore"}
          </button>
        </div>
      </div>}
    </div>
  );
}
