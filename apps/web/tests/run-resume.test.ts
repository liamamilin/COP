import { describe, expect, it } from "vitest";

import { decideResume } from "../lib/run-resume";
import type { GenerationRun } from "../lib/generation-api";

function run(overrides: Partial<GenerationRun>): GenerationRun {
  return {
    id: "run-1",
    project_id: "project-1",
    status: "queued",
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

describe("decideResume", () => {
  it("shows the start form when the project has never run", () => {
    expect(decideResume([])).toEqual({ kind: "idle" });
  });

  it("attaches to a running run and streams it", () => {
    const decision = decideResume([run({ status: "running" })]);
    expect(decision.kind).toBe("attach");
    expect(decision.kind === "attach" && decision.stream).toBe(true);
  });

  it("attaches to a queued run and streams it", () => {
    const decision = decideResume([run({ status: "queued" })]);
    expect(decision.kind === "attach" && decision.stream).toBe(true);
  });

  it.each(["completed", "needs_attention", "failed", "cancelled"] as const)(
    "attaches to a finished %s run without reopening a stream",
    (status) => {
      const decision = decideResume([run({ status })]);
      expect(decision.kind).toBe("attach");
      expect(decision.kind === "attach" && decision.stream).toBe(false);
    },
  );

  it("uses the newest run, not the oldest", () => {
    const decision = decideResume([
      run({ id: "newest", status: "running" }),
      run({ id: "older", status: "failed" }),
    ]);
    expect(decision.kind === "attach" && decision.run.id).toBe("newest");
  });
});
