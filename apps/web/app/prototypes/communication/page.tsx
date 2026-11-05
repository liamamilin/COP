import type { COPArtifact } from "@cop-studio/cop-types";
import type { LearningUnit } from "@cop-studio/cop-types/learning-unit";
import Link from "next/link";

import artifact from "../../../../../fixtures/communication-basics-cop.json";
import lesson from "../../../../../fixtures/communication-basics-learning-unit.json";
import manifest from "../../../../../fixtures/communication-basics-learning-unit.manifest.json";
import { LearningUnitReader } from "../../../components/learning-unit-reader";
import { learningUnitBinding } from "../../../lib/learning-unit-binding";

/** Local authored candidate. Never imports a published project or writes its data. */
export default function CommunicationPrototypePage() {
  const unit = lesson as LearningUnit;
  const source = artifact as COPArtifact;
  return <>
    <nav className="content-wrap" aria-label="Prototype navigation">
      <Link href="/">← All projects</Link>{" · "}<Link href="/prototypes/learning-unit">Basic learning-unit experiment</Link>
    </nav>
    <LearningUnitReader unit={unit} artifact={source} unitHash={manifest.unit_sha256} bindingValid={learningUnitBinding(unit, source, manifest)} />
  </>;
}
