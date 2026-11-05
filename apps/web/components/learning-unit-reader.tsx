"use client";

import type { COPArtifact } from "@cop-studio/cop-types";
import type { LearningQuestion, LearningUnit } from "@cop-studio/cop-types/learning-unit";
import { useRef, useState } from "react";

import {
  appliesToPath, emptyResponse, exportObservation, newObservation, observationKey, parseObservation,
  type LearningObservation, type QuestionResponse,
} from "../lib/learning-observation";
import { CopyButton } from "./copy-button";
import { ReasoningWalkthrough, TeachingOrientation } from "./teaching-explanation";
import styles from "./learning-unit-reader.module.css";

type BoundDetail = {
  title?: string;
  action?: string;
  command?: string;
  expected_result?: string;
  caution?: string;
};

/**
 * A teaching-owned method renderer.
 *
 * The source text still comes from the bound artifact, but this intentionally
 * does not import the project's Stage renderer. A future project display change
 * must not silently alter what a learner sees here.
 */
function BoundMethod({ detail }: { detail: BoundDetail }) {
  return <div className={styles.methodCard} data-bound-method>
    {detail.title && <h4>{detail.title}</h4>}
    {detail.action && <p>{detail.action}</p>}
    {detail.command && <div className={styles.code}>
      <div className={styles.codeHead}><span>Code / command</span><CopyButton text={detail.command} /></div>
      <pre><code>{detail.command}</code></pre>
    </div>}
    {detail.expected_result && <p className={styles.expected}><strong>You should see</strong> {detail.expected_result}</p>}
    {detail.caution && <p className={styles.caution}><strong>Watch out</strong> {detail.caution}</p>}
  </div>;
}

function Question({ question, response, onChange }: {
  question: LearningQuestion; response: QuestionResponse; onChange: (value: QuestionResponse) => void;
}) {
  return <section className={styles.question} aria-labelledby={`question-${question.id}`}>
    <p className={styles.kicker}>{question.kind.toUpperCase()} · UNGRADED</p>
    <h3 id={`question-${question.id}`}>{question.prompt}</h3>
    <label><span id={`response-label-${question.id}`}>Your response</span><textarea aria-labelledby={`response-label-${question.id}`} maxLength={12000} rows={4} value={response.answer} onChange={(event) => onChange({ ...response, answer: event.target.value })} /></label>
    <label><span id={`help-label-${question.id}`}>Help used / where you got stuck</span><textarea aria-labelledby={`help-label-${question.id}`} maxLength={12000} rows={2} value={response.help_used} onChange={(event) => onChange({ ...response, help_used: event.target.value })} /></label>
    <p className={styles.note}>Try first. Viewing support is recorded in these local notes, not treated as failure or mastery.</p>
    {response.hints_revealed > 0 && <ol className={styles.hints}>{question.hints.slice(0, response.hints_revealed).map((hint) => <li key={hint}>{hint}</li>)}</ol>}
    <div className={styles.buttons}>
      {response.hints_revealed < question.hints.length && <button type="button" onClick={() => onChange({ ...response, hints_revealed: response.hints_revealed + 1 })}>Show next hint ({response.hints_revealed}/{question.hints.length})</button>}
      {!response.criteria_revealed && <button type="button" onClick={() => onChange({ ...response, criteria_revealed: true })}>Show review criteria</button>}
    </div>
    {response.criteria_revealed && <div className={styles.criteria}><h4>Review criteria · not an answer grade</h4><ul>{question.criteria.map((criterion) => <li key={criterion}>{criterion}</li>)}</ul></div>}
  </section>;
}

/** Presentation + explicit device notes only. Bound source methods are reused verbatim. */
export function LearningUnitReader({ unit, artifact, unitHash, bindingValid }: {
  unit: LearningUnit; artifact: COPArtifact; unitHash: string; bindingValid: boolean;
}) {
  const [record, setRecord] = useState(() => newObservation(unit, unitHash));
  const [index, setIndex] = useState(0);
  const [assessment, setAssessment] = useState(false);
  const [message, setMessage] = useState("");
  const heading = useRef<HTMLHeadingElement>(null);
  const importInput = useRef<HTMLInputElement>(null);

  if (!bindingValid) return <section className={styles.reader} role="alert"><h1>Lesson revision mismatch</h1><p>The lesson, source methods and structural check do not match. This reader will not combine them. Rebuild and review the sidecar before continuing.</p></section>;

  const pathId = record.active_path_id;
  const path = unit.paths.find((item) => item.id === pathId)!;
  const pathRecord = record.paths[pathId];
  const step = unit.steps[index];
  const stage = artifact.stages.find((item) => item.id === step.stage_ref)!;
  const outputs = Object.fromEntries(unit.outputs.map((item) => [item.id, item]));
  const entries = Object.fromEntries(unit.profile.resources.map((item) => [item.id, item]));
  const active = (ids: string[]) => appliesToPath(ids, pathId);

  function change(value: LearningObservation) { setRecord(value); setMessage("Unsaved changes · local session only"); }
  function response(question: LearningQuestion) { return pathRecord.responses[question.id] ?? emptyResponse(); }
  function updateResponse(question: LearningQuestion, value: QuestionResponse) {
    change({ ...record, paths: { ...record.paths, [pathId]: { ...pathRecord, responses: { ...pathRecord.responses, [question.id]: value } } } });
  }
  function navigate(next: number, toAssessment = false) {
    setIndex(next); setAssessment(toAssessment);
    // The stable heading gives keyboard users a destination when replacing a step.
    heading.current?.focus();
  }
  function save() {
    try {
      localStorage.setItem(observationKey(unit.unit_id), exportObservation(record));
      setMessage("Saved on this device · unverified self-report");
    } catch { setMessage("Unable to save on this device. Export your notes instead."); }
  }
  function load() {
    try {
      const raw = localStorage.getItem(observationKey(unit.unit_id));
      if (!raw) { setMessage("No saved notes on this device."); return; }
      setRecord(parseObservation(raw, unit, unitHash));
      setMessage("Loaded saved notes · unverified self-report");
    } catch { setMessage("Saved notes could not be loaded: storage is unavailable or the lesson revision/format differs. Current notes were kept."); }
  }
  function download() {
    const url = URL.createObjectURL(new Blob([exportObservation(record)], { type: "application/json" }));
    const link = document.createElement("a");
    link.href = url; link.download = `${unit.unit_id}-observations.json`; link.click();
    URL.revokeObjectURL(url);
    setMessage("Exported unverified notes. Review for private information before sharing.");
  }
  async function importNotes(file: File | undefined) {
    if (!file) return;
    try {
      if (file.size > 200000) throw new Error("Too large");
      const imported = parseObservation(await file.text(), unit, unitHash);
      setRecord(imported); setMessage("Imported notes · not saved on this device yet");
    } catch { setMessage("Import rejected: invalid notes or a different lesson revision. Current notes were kept."); }
    if (importInput.current) importInput.current.value = "";
  }

  return <main className={styles.reader}>
    <header className={styles.header}>
      <p className={styles.kicker}>LEARNING UNIT · EXPERIMENTAL · NOT PUBLISHED</p>
      <h1>{unit.title}</h1><p className={styles.outcome}>{unit.outcome}</p><p>{unit.task_brief}</p>
      <p className={styles.note}>A hand-authored teaching sample, not evidence of stable automatic generation or learning effectiveness. This page never runs commands, contacts a provider, or writes project progress.</p>
    </header>

    {unit.orientation && <div className={styles.orientation}><TeachingOrientation orientation={unit.orientation} /></div>}

    <section className={styles.start} aria-labelledby="entry-heading">
      <h2 id="entry-heading">Before you start</h2><p>{unit.profile.audience}</p>
      <div className={styles.profile}>
        <div><h3>Starting knowledge</h3><ul>{unit.profile.prior_knowledge.map((item) => <li key={item}>{item}</li>)}</ul></div>
        <div><h3>Environment</h3><ul>{unit.profile.environment.map((item) => <li key={item}>{item}</li>)}</ul></div>
      </div>
      <details><summary>Outside this unit</summary><ul>{unit.profile.exclusions.map((item) => <li key={item}>{item}</li>)}</ul></details>
      <label className={styles.pathLabel}>Learning path<select value={pathId} onChange={(event) => change({ ...record, active_path_id: event.target.value })}>{unit.paths.map((item) => <option key={item.id} value={item.id}>{item.label}</option>)}</select></label>
      <div className={styles.boundary} role="note"><strong>{path.goal_scope === "partial" ? "Partial goal · not full capability evidence" : "Full task path · results still need verification"}</strong><p>{path.description}</p><p>Network: {path.needs_network ? "required for some steps" : "not required"} · Cost: {path.may_cost ? "possible; separate explicit consent required before any paid command" : "no provider calls in this path"}</p></div>
      <details><summary>Required resources &amp; readiness checks</summary><dl>{unit.profile.resources.filter((item) => active(item.path_ids)).map((item) => <div key={item.id}><dt>{item.name}</dt><dd><p>{item.provenance}</p><p><strong>Check readiness</strong> {item.readiness_check}</p></dd></div>)}</dl></details>
    </section>

    <div className={styles.workspace}>
      <nav className={styles.route} aria-label="Learning unit steps"><h2>Task path</h2><p className={styles.note}>Navigation does not mark completion.</p><ol>{unit.steps.map((item, itemIndex) => <li key={item.stage_ref}><button type="button" aria-current={!assessment && itemIndex === index ? "step" : undefined} onClick={() => navigate(itemIndex)}><span>Step {itemIndex + 1}</span>{artifact.stages.find((source) => source.id === item.stage_ref)?.title}</button></li>)}</ol><button type="button" aria-current={assessment ? "step" : undefined} onClick={() => navigate(index, true)}>Explain, diagnose &amp; transfer</button></nav>
      <article className={styles.lesson} aria-labelledby="active-unit-heading">
        <p className={styles.kicker}>{assessment ? "ASSESSMENT · SELF-REPORT, NOT A GRADE" : `STEP ${index + 1} OF ${unit.steps.length}`}</p>
        <h2 id="active-unit-heading" ref={heading} tabIndex={-1}>{assessment ? "Explain, diagnose & transfer" : stage.title}</h2>
        {assessment ? <><p>Work without hints first. Record outside help and actual results; the application does not determine whether your answer is correct.</p>{unit.assessment.filter((item) => active(item.path_ids)).map((item) => <Question key={`${pathId}-${item.id}`} question={item} response={response(item)} onChange={(value) => updateResponse(item, value)} />)}</> : <>
          <p>{step.purpose}</p>
          <section><h3>Inputs · where they come from</h3><dl>{step.inputs.filter((item) => active(item.path_ids)).map((item) => {
            const output = item.kind === "output" ? outputs[item.ref] : undefined;
            const source = output ? artifact.stages.find((s) => s.id === output.producer_stage_ref)?.title : entries[item.ref]?.provenance;
            return <div key={`${item.kind}-${item.ref}`}><dt>{output?.name ?? entries[item.ref]?.name}</dt><dd><p><strong>From</strong> {source}</p><p>{item.why_needed}</p><p><strong>Check before continuing</strong> {item.readiness_check}</p></dd></div>;
          })}</dl></section>
          <section><h3>Understand the ideas</h3>{step.concepts.map((item) => <div className={styles.concept} key={item.concept_ref}><h4>{artifact.concepts.find((c) => c.id === item.concept_ref)?.name}</h4><p>{item.plain_language}</p><p><strong>Concrete example</strong> {item.concrete_example}</p><p><strong>Not the same as</strong> {item.contrast}</p><p><strong>Why here</strong> {item.why_here}</p></div>)}</section>
          <section><h3>Why the operation works</h3>{step.causal_chain.map((item, linkIndex) => <dl className={styles.causal} key={linkIndex}><div><dt>Before</dt><dd>{item.before}</dd></div><div><dt>Action</dt><dd>{item.action}</dd></div><div><dt>Because</dt><dd>{item.because}</dd></div><div><dt>After</dt><dd>{item.after}</dd></div></dl>)}</section>
          <ReasoningWalkthrough moves={step.reasoning ?? []} sources={unit.sources} />
          <section><h3>Follow the method</h3><p className={styles.note}>Instructions from the bound source artifact, not execution records. Review before running in your own environment. Never paste credentials into these notes.</p><div>{step.methods.filter((item) => !item.optional && active(item.path_ids)).map((item) => <div className={styles.method} key={item.detail_index}><p className={styles.teachingNote}>{item.teaching_note}</p><BoundMethod detail={stage.implementation_details![item.detail_index]} /></div>)}</div>
            {step.methods.some((item) => item.optional && active(item.path_ids)) && <details><summary>Optional methods · not required for this path</summary><div>{step.methods.filter((item) => item.optional && active(item.path_ids)).map((item) => <div className={styles.method} key={item.detail_index}><p>{item.teaching_note}</p><BoundMethod detail={stage.implementation_details![item.detail_index]} /></div>)}</div></details>}
          </section>
          <section className={styles.example}><h3>Worked case · illustration, not your result</h3><ol>{step.worked_case.walkthrough.map((item) => <li key={item}>{item}</li>)}</ol><p>{step.worked_case.observation}</p></section>
          <section><h3>Outputs &amp; checks</h3>{step.checks.filter((item) => active(item.path_ids)).map((item, checkIndex) => <div className={styles.check} key={checkIndex}><h4>{outputs[item.output_ref]?.name}</h4><p>{outputs[item.output_ref]?.description}</p><dl><div><dt>Do</dt><dd>{item.instruction}</dd></div><div><dt>Expected</dt><dd>{item.expected}</dd></div><div><dt>Why this check</dt><dd>{item.why}</dd></div><div><dt>Does not prove</dt><dd>{item.limitation}</dd></div><div><dt>If it fails</dt><dd>{item.on_failure}</dd></div></dl></div>)}
            <label>Observed result / mismatch<textarea rows={3} maxLength={12000} value={pathRecord.observations[step.stage_ref] ?? ""} onChange={(event) => change({ ...record, paths: { ...record.paths, [pathId]: { ...pathRecord, observations: { ...pathRecord.observations, [step.stage_ref]: event.target.value } } } })} /></label>
          </section>
          <Question key={`${pathId}-${step.practice.id}`} question={step.practice} response={response(step.practice)} onChange={(value) => updateResponse(step.practice, value)} />
        </>}
        <div className={styles.navigation}><button type="button" disabled={index === 0 && !assessment} onClick={() => navigate(assessment ? index : index - 1)}>Previous step</button><button type="button" disabled={assessment} onClick={() => index + 1 < unit.steps.length ? navigate(index + 1) : navigate(index, true)}>{index + 1 < unit.steps.length ? "Next step" : "Open assessment"}</button></div>
      </article>
    </div>

    <section className={styles.notes} aria-labelledby="notes-heading"><h2 id="notes-heading">Your observations · local only</h2><p>No automatic grading or mastery claim. Notes are not sent to the project API. Save only on a trusted device; exported notes may contain what you type. Do not enter keys, tokens, private endpoints or personal data.</p><div className={styles.buttons}><button type="button" onClick={save}>Save on this device</button><button type="button" onClick={load}>Load saved notes</button><button type="button" onClick={download}>Export notes</button><label className={styles.import}>Import notes<input ref={importInput} type="file" accept="application/json,.json" onChange={(event) => void importNotes(event.target.files?.[0])} /></label></div><p role="status" aria-live="polite">{message}</p></section>
    <footer className={styles.footer}><h2>Evidence &amp; limits</h2><p>Content binding and a structure-only check match this lesson revision. They do not verify factual correctness, execution, understanding or transfer.</p><ul>{unit.limitations.map((item) => <li key={item}>{item}</li>)}</ul><section><h3>Sources &amp; what they support</h3><ul>{unit.sources.map((item) => <li id={`unit-source-${item.id}`} key={item.id}><a href={item.url} target="_blank" rel="noreferrer">{item.title} ↗</a><p>{item.scope}</p></li>)}</ul></section></footer>
  </main>;
}
