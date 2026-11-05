import { ApiError, createDraftFromRun, getDraft, type DraftDetail } from "./api";

/** Candidate-to-draft handoff, independent of routing and rendering.
 * A conflict is not proof that the existing draft belongs to this run.
 */
export async function prepareGenerationDraft(
  projectId: string, runId: string,
): Promise<{ draft: DraftDetail; matchesRun: boolean }> {
  let draft: DraftDetail | null;
  try {
    draft = await createDraftFromRun(projectId, runId);
  } catch (cause) {
    if (!(cause instanceof ApiError) || cause.status !== 409) throw cause;
    draft = await getDraft(projectId);
  }
  if (!draft || draft.project_id !== projectId) {
    throw new Error("The candidate is saved, but its draft could not be opened. Please try again.");
  }
  return { draft, matchesRun: draft.source_run_id === runId };
}
