import { describe, expect, it } from "vitest";

import {
  describeRunStatus,
  isTerminal,
  type GenerationRun,
} from "../lib/generation-api";

function run(overrides: Partial<GenerationRun> = {}): GenerationRun {
  return {
    id: "run-1",
    project_id: "project-1",
    status: "completed",
    requested_mode: "standard",
    base_version_id: null,
    started_at: null,
    completed_at: null,
    heartbeat_at: null,
    worker_id: null,
    cancel_requested: false,
    error_code: null,
    error_message: null,
    metrics: {},
    created_at: null,
    updated_at: null,
    ...overrides,
  };
}

describe("run status", () => {
  it("treats only terminal states as finished", () => {
    expect(isTerminal("completed")).toBe(true);
    expect(isTerminal("needs_attention")).toBe(true);
    expect(isTerminal("failed")).toBe(true);
    expect(isTerminal("cancelled")).toBe(true);
    expect(isTerminal("queued")).toBe(false);
    expect(isTerminal("running")).toBe(false);
  });
});

describe("describeRunStatus", () => {
  it("never implies publishing happened on a completed run", () => {
    const status = describeRunStatus(run({ status: "completed" }));
    expect(status.tone).toBe("ok");
    expect(status.detail).toMatch(/review/i);
    expect(status.detail).toMatch(/your decision/i);
  });

  it("tells the user their work survives a failure", () => {
    const status = describeRunStatus(run({ status: "failed" }));
    expect(status.tone).toBe("error");
    expect(status.detail).toMatch(/unchanged/i);
  });

  it("reports needs_attention as actionable, not as a hard failure", () => {
    const status = describeRunStatus(run({ status: "needs_attention" }));
    expect(status.tone).toBe("attention");
    expect(status.headline).toMatch(/attention/i);
    expect(status.detail).toMatch(/checkpoint/i);
  });

  it("prefers the server-provided error message when present", () => {
    const status = describeRunStatus(
      run({ status: "failed", error_message: "Provider rejected the API key" }),
    );
    expect(status.detail).toBe("Provider rejected the API key");
  });

  it("reassures on cancellation that nothing was lost", () => {
    const status = describeRunStatus(run({ status: "cancelled" }));
    expect(status.detail).toMatch(/unchanged/i);
  });
});
