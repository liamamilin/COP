import type { Practice } from "@cop-studio/cop-types";

export function PracticeCard({ practice }: { practice: Practice }) {
  return (
    <section className="practice-card">
      <div className="practice-heading">
        <span>MINIMAL PRACTICE</span>
        <b>{practice.instructions.length} moves</b>
      </div>
      <h3>{practice.title}</h3>
      <ol>
        {practice.instructions.map((instruction) => <li key={instruction}>{instruction}</li>)}
      </ol>
      <div className="expected-outcome">
        <small>EXPECTED OUTCOME</small>
        <p>{practice.expected_outcome}</p>
      </div>
    </section>
  );
}

