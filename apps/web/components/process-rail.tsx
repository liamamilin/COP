import type { COPArtifact, MainProcess } from "@cop-studio/cop-types";
import Link from "next/link";

import { artifactSelectors } from "../lib/artifact-selectors";

interface ProcessRailProps {
  artifact: COPArtifact;
  process: MainProcess;
  projectId: string;
  compact?: boolean;
}

export function ProcessRail({ artifact, process, projectId, compact }: ProcessRailProps) {
  const stages = artifactSelectors.getStagesForProcess(artifact, process);
  const foundation = process.start.ref
    ? artifact.shared_foundations.find((item) => item.id === process.start.ref)
    : undefined;

  return (
    <div className={compact ? "process-rail compact" : "process-rail"}>
      <div className="process-node foundation-node">
        <span className="node-index">00</span>
        <div>
          <small>{foundation ? "SHARED FOUNDATION" : "ZERO STATE"}</small>
          <strong>{foundation?.title ?? "Start from zero"}</strong>
        </div>
      </div>
      {stages.map((stage, index) => (
        <div className="process-step" key={stage.id}>
          <span className="process-connector" aria-hidden="true">↓</span>
          <Link
            className="process-node stage-node"
            href={`/projects/${projectId}/stages/${encodeURIComponent(stage.id)}`}
          >
            <span className="node-index">{String(index + 1).padStart(2, "0")}</span>
            <div>
              <small>STAGE {index + 1}</small>
              <strong>{stage.title}</strong>
              {!compact && <p>{stage.local_goal}</p>}
            </div>
            <span className="node-arrow">↗</span>
          </Link>
        </div>
      ))}
      <div className="process-step">
        <span className="process-connector" aria-hidden="true">↓</span>
        <div className="process-node outcome-node">
          <span className="node-index">✓</span>
          <div>
            <small>OUTCOME</small>
            <strong>{process.outcome}</strong>
          </div>
        </div>
      </div>
    </div>
  );
}

