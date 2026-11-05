import type { ReasoningMove, UnitOrientation, UnitSource } from "@cop-studio/cop-types/learning-unit";

/** Authored explanations only. No runtime inference, grading, or project state. */
export function TeachingOrientation({ orientation }: { orientation: UnitOrientation }) {
  return <section aria-labelledby="teaching-question" data-teaching-orientation>
    <p>THE QUESTION BEHIND THIS UNIT</p>
    <h2 id="teaching-question">{orientation.question}</h2>
    <h3>Why this learning route?</h3>
    <p>{orientation.why_this_route}</p>
    <h3>One running case · illustration</h3>
    <p>{orientation.running_case}</p>
    <h4>Given facts in this case</h4>
    <ul>{orientation.case_facts.map((fact) => <li key={fact}>{fact}</li>)}</ul>
    <h4>Not yet known</h4>
    <ul>{orientation.case_unknowns.map((unknown) => <li key={unknown}>{unknown}</li>)}</ul>
    <h3>How the questions connect</h3>
    <ol>{orientation.route.map((item) => <li key={item.stage_ref}>
      <strong>{item.question}</strong>
      <p><strong>Why now</strong> {item.why_now}</p>
      <p><strong>What remains to investigate</strong> {item.next_gap}</p>
    </li>)}</ol>
  </section>;
}

export function ReasoningWalkthrough({ moves, sources }: { moves: ReasoningMove[]; sources: UnitSource[] }) {
  if (!moves.length) return null;
  return <section data-reasoning-walkthrough>
    <h3>Work through the reasoning</h3>
    <p>Follow the move from an observation to an interpretation. The limitation is part of the conclusion, not optional fine print.</p>
    {moves.map((move, index) => <div key={index}>
      <h4>Reasoning move {index + 1}</h4>
      <dl>
        <dt>What we observe</dt><dd>{move.observation}</dd>
        <dt>What we infer</dt><dd>{move.inference}</dd>
        <dt>Why that inference is reasonable</dt><dd>{move.warrant}</dd>
        <dt>What it does not establish</dt><dd>{move.limitation}</dd>
      </dl>
      <p>Source scope: {move.source_ids.map((id, sourceIndex) => {
        const source = sources.find((item) => item.id === id);
        return <span key={id}>{sourceIndex > 0 && " · "}<a href={`#unit-source-${id}`}>{source?.title ?? id}</a></span>;
      })}</p>
    </div>)}
  </section>;
}
