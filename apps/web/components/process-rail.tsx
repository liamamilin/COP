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
      {/*
        The Foundation is the start of the line, so it has to be reachable the
        same way every other Stage is. It was a plain div, which left the two
        setup Stages -- the ones that install the library and set the API key --
        reachable only by typing a URL, and it carried no arrow to signal that.
      */}
      {foundation && foundation.stage_refs.length > 0 ? (
        <div className="process-step">
          <Link
            className="process-node foundation-node stage-node"
            href={`/projects/${projectId}/stages/${encodeURIComponent(foundation.stage_refs[0])}`}
          >
            <span className="node-index">00</span>
            <div>
              <small>SHARED FOUNDATION · {foundation.stage_refs.length} STAGES</small>
              <strong>{foundation.title}</strong>
            </div>
            <span className="node-arrow">↗</span>
          </Link>
        </div>
      ) : (
        <div className="process-node foundation-node">
          <span className="node-index">00</span>
          <div>
            <small>ZERO STATE</small>
            <strong>Start from zero</strong>
          </div>
        </div>
      )}
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

