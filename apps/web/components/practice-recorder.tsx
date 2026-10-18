"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";

import { PracticeCard } from "./practice-card";
import {
  ApiError,
  putLearningProgress,
  type PracticeProgress,
} from "../lib/api";
import type { Practice } from "@cop-studio/cop-types";

/**
 * A Practice the learner can complete, on a read-only page.
 *
 * The Goal and Main Process pages render a Practice for context, and R5 makes it
 * interactive there too rather than sending the learner to Learn Mode to record
 * it. A checkbox that only works in one place is a dead end in the other.
 */
export function PracticeRecorder({
  projectId,
  versionId,
  goalId,
  practice,
  progress,
}: {
  projectId: string;
  versionId: string;
  goalId: string;
  practice: Practice;
  progress: PracticeProgress | null;
}) {
  const router = useRouter();
  const [pending, setPending] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [local, setLocal] = useState<PracticeProgress | null>(null);

  const current = local ?? progress;

  async function record(body: {
    kind: "practice" | "checkpoint";
    status: "in_progress" | "completed";
    stage_id?: string;
    notes?: string;
  }) {
    setPending(true);
    setError(null);
    try {
      await putLearningProgress(projectId, {
        version_id: versionId,
        kind: body.kind,
        goal_id: goalId,
        stage_id: body.stage_id ?? null,
        status: body.status,
        notes: body.notes ?? null,
      });
      setLocal(null);
      router.refresh();
    } catch (cause) {
      setError(
        cause instanceof ApiError ? cause.message : "Practice progress could not be saved.",
      );
    } finally {
      setPending(false);
    }
  }

  return (
    <>
      <PracticeCard
        disabled={pending}
        onAnswerCheckpoint={(question, answer) =>
          void record({ kind: "checkpoint", status: "completed", stage_id: question, notes: answer })
        }
        onRecordPractice={(status) => void record({ kind: "practice", status })}
        practice={practice}
        progress={current}
      />
      {error && (
        <p className="form-error" role="alert">
          {error}
        </p>
      )}
    </>
  );
}
