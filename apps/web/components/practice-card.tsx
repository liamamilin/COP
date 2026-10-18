"use client";

import { useState } from "react";

import type { Practice } from "@cop-studio/cop-types";

import type { CheckpointProgress, PracticeProgress } from "../lib/api";

/**
 * A Minimal Practice the learner can actually complete.
 *
 * M7 rendered the instructions and the checkpoint questions and nothing else, so
 * the exercise was read-only: a learner could work through a Practice and the app
 * had no way to know. R5 gives it a status and an answer box per question.
 *
 * `progress` is the server's view. Local state exists only so a keystroke does
 * not wait on a round trip; the server value always wins on the next render, so
 * a failed save cannot leave a false "completed" on screen.
 */
export function PracticeCard({
  practice,
  progress,
  onRecordPractice,
  onAnswerCheckpoint,
  disabled,
}: {
  practice: Practice;
  progress: PracticeProgress | null;
  onRecordPractice: (status: "in_progress" | "completed") => void;
  onAnswerCheckpoint: (question: string, answer: string) => void;
  disabled?: boolean;
}) {
  const status = progress?.status ?? "not_started";
  const [drafts, setDrafts] = useState<Record<string, string>>({});

  // The server is the authority on which questions exist. Falling back to the
  // artifact's list is for the brief window before the first progress read, and
  // every question is unanswered there, which is correct rather than optimistic.
  const checkpoints: CheckpointProgress[] =
    progress?.checkpoints ??
    (practice.checkpoint_questions ?? []).map((question) => ({
      question,
      answer: null,
      updated_at: null,
    }));

  const answered = checkpoints.filter((item) => (item.answer ?? "").trim().length > 0);
  const allAnswered = answered.length === checkpoints.length && checkpoints.length > 0;

  return (
    <section className="practice-card" data-practice-status={status}>
      <div className="practice-heading">
        <span>MINIMAL PRACTICE</span>
        <b>{practice.instructions.length} moves</b>
      </div>
      <h3>{practice.title}</h3>
      <p className="practice-status">
        {status === "completed"
          ? "Completed"
          : status === "in_progress"
            ? "In progress"
            : "Not started"}
      </p>
      <ol>
        {practice.instructions.map((instruction) => (
          <li key={instruction}>{instruction}</li>
        ))}
      </ol>
      <div className="expected-outcome">
        <small>EXPECTED OUTCOME</small>
        <p>{practice.expected_outcome}</p>
      </div>

      {checkpoints.length > 0 && (
        <div className="practice-checkpoints">
          <small>
            CHECKPOINTS · {answered.length} of {checkpoints.length} answered
          </small>
          {checkpoints.map((item) => {
            const value = drafts[item.question] ?? item.answer ?? "";
            return (
              <label key={item.question}>
                <span>{item.question}</span>
                <textarea
                  disabled={disabled}
                  onChange={(event) =>
                    setDrafts((current) => ({ ...current, [item.question]: event.target.value }))
                  }
                  onBlur={() => {
                    // Saved on blur rather than per keystroke: a round trip per
                    // character, and a save that fails while the user is still
                    // typing, help nobody.
                    if ((item.answer ?? "") !== value.trim()) {
                      onAnswerCheckpoint(item.question, value.trim());
                    }
                  }}
                  placeholder="Your answer"
                  rows={3}
                  value={value}
                />
              </label>
            );
          })}
        </div>
      )}

      <div className="practice-actions">
        {status !== "completed" && (
          <button
            className="secondary-button"
            disabled={disabled}
            onClick={() => onRecordPractice("in_progress")}
            type="button"
          >
            Mark as started
          </button>
        )}
        <button
          className="primary-button"
          disabled={disabled || (status !== "completed" && !allAnswered)}
          onClick={() => onRecordPractice("completed")}
          type="button"
        >
          {status === "completed" ? "Completed" : "Mark practice complete"}
        </button>
        {status !== "completed" && !allAnswered && (
          <small className="muted-note">
            Answer every checkpoint question to complete this practice.
          </small>
        )}
      </div>
    </section>
  );
}
