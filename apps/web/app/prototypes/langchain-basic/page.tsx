import type { COPArtifact } from "@cop-studio/cop-types";
import Link from "next/link";

import prototype from "../../../../../fixtures/langchain-basic-cop.json";
import sourceSummaries from "../../../../../fixtures/langchain-basic-sources.json";
import { BasicPrototypeView } from "../../../components/basic-prototype-view";
import type { ResolvedSource } from "../../../components/evidence-panel";

export default function BasicPrototypePage() {
  const artifact = prototype as COPArtifact;
  const sources: Record<string, ResolvedSource> = Object.fromEntries(sourceSummaries.map((source) => [source.id, {
    id: source.id, title: source.title, type: "text", uri: source.original_uri, status: "manual-summary",
  }]));
  const practice = artifact.practices[0];
  return (
    <main className="content-wrap narrow-content">
      <header className="page-header detail-header">
        <p className="eyebrow">LOCAL PROTOTYPE · READ ONLY · NOT PUBLISHED</p>
        <h1>{artifact.domain.name}</h1>
        <p className="lead-copy">{artifact.goals[0].outcome}</p>
        <p>{artifact.domain.scope}</p>
        <p className="muted-note">这里不会创建项目、保存学习进度或运行代码。代码需在你自己的独立环境执行；真实调用可能收费。</p>
        <p><Link href="/">← All projects</Link></p>
      </header>
      <section className="reading-section">
        <p className="eyebrow">MENTAL MODEL</p>
        <p>{artifact.mental_model.summary}</p>
        <p>{artifact.mental_model.flow?.join(" → ")}</p>
      </section>
      <BasicPrototypeView artifact={artifact} sources={sources} />
      <section className="practice-card" id="prototype-practice">
        <p className="eyebrow">MINIMAL PRACTICE · READ ONLY</p>
        <h2>{practice.title}</h2>
        <ol>{practice.instructions.map((item) => <li key={item}>{item}</li>)}</ol>
        <p>{practice.expected_outcome}</p>
        <h3>Checkpoints</h3>
        <ul className="prototype-checkpoints">{practice.checkpoint_questions?.map((item) => <li key={item}>{item}</li>)}</ul>
      </section>
      <section className="reading-section">
        <p className="eyebrow">CONCEPTS & OPERATIONS</p>
        {artifact.concepts.map((concept) => <div id={`concept-${concept.id}`} key={concept.id}><h3>{concept.name}</h3><p>{concept.definition}</p><p>{concept.role}</p></div>)}
        {artifact.operations.map((operation) => <div id={`operation-${operation.id}`} key={operation.id}><h3>{operation.name}</h3><p>{operation.definition}</p><ul>{operation.common_failures?.map((item) => <li key={item}>{item}</li>)}</ul></div>)}
      </section>
      <section className="reading-section">
        <p className="eyebrow">SOURCES · HUMAN SUMMARIES, NOT WEB SNAPSHOTS</p>
        {sourceSummaries.map((source) => (
          <div id={`source-${source.id}`} key={source.id}>
            <h3><a href={source.original_uri} target="_blank" rel="noreferrer">{source.title} ↗</a></h3>
            <p>{source.text}</p>
          </div>
        ))}
      </section>
      <section className="reading-section">
        <p className="eyebrow">NEXT & BOUNDARIES</p>
        <ul>{artifact.domain.non_goals?.map((item) => <li key={item}>{item}</li>)}</ul>
        {artifact.expansion_map.map((item) => <div key={item.title}><h3>{item.title}</h3><p>{item.description}</p></div>)}
      </section>
    </main>
  );
}
