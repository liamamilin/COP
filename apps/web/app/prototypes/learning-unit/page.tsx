import type { COPArtifact } from "@cop-studio/cop-types";
import type { LearningUnit } from "@cop-studio/cop-types/learning-unit";
import Link from "next/link";

import artifact from "../../../../../fixtures/langchain-basic-cop.json";
import lesson from "../../../../../fixtures/langchain-basic-learning-unit.json";
import manifest from "../../../../../fixtures/langchain-basic-learning-unit.manifest.json";
import { LearningUnitReader } from "../../../components/learning-unit-reader";
import { learningUnitBinding } from "../../../lib/learning-unit-binding";

export default function LearningUnitPrototypePage() {
  const unit = lesson as LearningUnit;
  const source = artifact as COPArtifact;
  return <>
    <nav className="content-wrap" aria-label="Prototype navigation"><Link href="/">← All projects</Link>{" · "}<Link href="/prototypes/langchain-basic">Source COP prototype</Link>{" · "}<Link href="/prototypes/communication">Communication reasoning sample</Link></nav>
    <LearningUnitReader unit={unit} artifact={source} unitHash={manifest.unit_sha256} bindingValid={learningUnitBinding(unit, source, manifest)} />
  </>;
}
