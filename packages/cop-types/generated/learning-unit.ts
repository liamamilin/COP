/* Generated from schemas/learning-unit.experimental.schema.json. Do not edit by hand. */

export interface CausalLink {
  concept_ref: string;
  operation_ref: string;
  before: string;
  action: string;
  because: string;
  after: string;
}

export interface ConceptExplanation {
  concept_ref: string;
  plain_language: string;
  concrete_example: string;
  contrast: string;
  why_here: string;
}

export interface DetailRef {
  stage_ref: string;
  detail_index: number;
}

export interface EntryResource {
  id: string;
  name: string;
  provenance: string;
  readiness_check: string;
  path_ids: string[];
}

export interface InputBinding {
  kind: "entry" | "output";
  ref: string;
  why_needed: string;
  readiness_check: string;
  path_ids: string[];
}

export interface LearnerProfile {
  audience: string;
  prior_knowledge: string[];
  environment: string[];
  exclusions: string[];
  resources: EntryResource[];
}

export interface LearningPath {
  id: string;
  label: string;
  description: string;
  goal_scope: "partial" | "full";
  needs_network: boolean;
  may_cost: boolean;
}

export interface LearningQuestion {
  id: string;
  kind: "predict" | "explain" | "diagnose" | "transfer";
  prompt: string;
  hints: string[];
  criteria: string[];
  stage_refs: string[];
  path_ids: string[];
}

export interface ReasoningMove {
  observation: string;
  inference: string;
  warrant: string;
  limitation: string;
  source_ids: string[];
}

export interface RouteExplanation {
  stage_ref: string;
  question: string;
  builds_on: string[];
  why_now: string;
  next_gap: string;
}

export interface UnitBinding {
  artifact_sha256: string;
  goal_ref: string;
  process_ref: string;
}

export interface UnitCheck {
  output_ref: string;
  instruction: string;
  expected: string;
  why: string;
  limitation: string;
  on_failure: string;
  path_ids: string[];
}

export interface UnitMethod {
  detail_index: number;
  teaching_note: string;
  optional: boolean;
  path_ids: string[];
}

export interface UnitOrientation {
  question: string;
  why_this_route: string;
  running_case: string;
  case_facts: string[];
  case_unknowns: string[];
  route: RouteExplanation[];
}

export interface UnitOutput {
  id: string;
  name: string;
  description: string;
  producer_stage_ref: string;
  kind: "file" | "value" | "evidence" | "private";
  persistence: "durable" | "process";
  format: "python" | "json" | "text" | "unspecified";
  content_ref: DetailRef | null;
  path_ids: string[];
}

export interface UnitSource {
  id: string;
  title: string;
  url: string;
  scope: string;
}

export interface UnitStep {
  stage_ref: string;
  purpose: string;
  inputs: InputBinding[];
  concepts: ConceptExplanation[];
  causal_chain: CausalLink[];
  methods: UnitMethod[];
  output_refs: string[];
  worked_case: WorkedCase;
  checks: UnitCheck[];
  practice: LearningQuestion;
  reasoning?: ReasoningMove[];
}

export interface WorkedCase {
  kind: "illustration";
  input_refs: string[];
  output_refs: string[];
  walkthrough: string[];
  observation: string;
}

export interface LearningUnit {
  schema_version: "0.1-experimental";
  unit_id: string;
  title: string;
  outcome: string;
  task_brief: string;
  binding: UnitBinding;
  profile: LearnerProfile;
  paths: LearningPath[];
  outputs: UnitOutput[];
  steps: UnitStep[];
  assessment: LearningQuestion[];
  sources: UnitSource[];
  limitations: string[];
  orientation?: UnitOrientation | null;
}
