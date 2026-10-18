/* Generated from schemas/cop-artifact.schema.json. Do not edit by hand. */

export interface EvidenceRef {
  source_id: string;
  segment_id?: string;
  quote_hint?: string;
}

export interface ImplementationDetail {
  title: string;
  action?: string;
  command?: string;
  expected_result?: string;
  caution?: string;
}

export interface Example {
  summary: string;
  input?: string;
  output?: string;
  note?: string;
}

export interface Goal {
  id: string;
  title: string;
  outcome: string;
  why_it_matters?: string;
  prerequisite_goal_refs?: string[];
  evidence_refs?: EvidenceRef[];
}

export interface SharedFoundation {
  id: string;
  title: string;
  stage_refs: string[];
}

export interface MainProcess {
  id: string;
  goal_ref: string;
  title: string;
  start: {
    type: "zero" | "foundation";
    ref?: string | null;
  };
  stage_refs: string[];
  outcome: string;
  practice_ref?: string | null;
}

export interface Stage {
  id: string;
  title: string;
  local_goal: string;
  why_it_exists?: string;
  local_outcome?: string;
  concept_refs: string[];
  operation_refs: string[];
  branch_refs?: string[];
  implementation_details?: ImplementationDetail[];
  example?: Example | null;
  evidence_refs?: EvidenceRef[];
}

export interface Concept {
  id: string;
  name: string;
  definition: string;
  role: string;
  related_concept_refs?: string[];
  key_operation_refs?: string[];
}

export interface Operation {
  id: string;
  name: string;
  definition: string;
  purpose?: string;
  acts_on_concept_refs?: string[];
  common_failures?: string[];
}

export interface Branch {
  id: string;
  type: "alternative" | "extension";
  title: string;
  parent_stage_ref?: string | null;
  parent_process_ref?: string | null;
  description?: string;
}

export interface Practice {
  id: string;
  title: string;
  goal_ref: string;
  instructions: string[];
  expected_outcome: string;
  checkpoint_questions?: string[];
}

export interface ExpansionItem {
  title: string;
  description?: string;
  from_goal_ref?: string | null;
}

export interface COPArtifact {
  schema_version: "0.1";
  artifact_id: string;
  domain: {
    name: string;
    scope: string;
    target_user: string;
    non_goals?: string[];
  };
  mental_model: {
    summary: string;
    flow?: string[];
  };
  goals: Goal[];
  shared_foundations: SharedFoundation[];
  main_processes: MainProcess[];
  stages: Stage[];
  concepts: Concept[];
  operations: Operation[];
  branches: Branch[];
  practices: Practice[];
  expansion_map: ExpansionItem[];
  metadata: {
    language?: string;
    generated_at?: string;
    generator?: string;
    source_ids?: string[];
  };
}
