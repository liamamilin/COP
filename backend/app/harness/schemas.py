"""JSON Schemas describing each Harness step's structured output.

These schemas are the contract between the LLM, the mock provider, and
validation. The `title` is also the routing key the mock provider uses to pick
a deterministic response, so titles must be unique and stable.
"""

from typing import Any

EVIDENCE_REF = {
    "type": "object",
    "properties": {
        "source_id": {"type": "string"},
        "segment_id": {"type": "string"},
        "quote_hint": {"type": "string"},
    },
    "required": ["source_id"],
    "additionalProperties": True,
}

INTAKE_SCHEMA: dict[str, Any] = {
    "title": "H00Intake",
    "type": "object",
    "properties": {
        "topic": {"type": "string"},
        "scope_hint": {"type": "string"},
        "target_outcomes": {"type": "array", "items": {"type": "string"}},
        "learner_level": {"type": "string"},
        "language": {"type": "string"},
        "depth": {"type": "string"},
        "source_ids": {"type": "array", "items": {"type": "string"}},
    },
    "required": ["topic", "target_outcomes", "learner_level", "language", "depth"],
    "additionalProperties": True,
}

SCOPE_SCHEMA: dict[str, Any] = {
    "title": "H10ScopeResolution",
    "type": "object",
    "properties": {
        "domain": {"type": "string"},
        "scope": {"type": "string"},
        "target_user": {"type": "string"},
        "non_goals": {"type": "array", "items": {"type": "string"}},
        "ambiguity_notes": {"type": "array", "items": {"type": "string"}},
    },
    "required": ["domain", "scope", "target_user"],
    "additionalProperties": True,
}

RESEARCH_BRIEF_SCHEMA: dict[str, Any] = {
    "title": "H20ResearchBrief",
    "type": "object",
    "properties": {
        "domain_purpose": {"type": "string"},
        "capability_candidates": {"type": "array", "items": {"type": "string"}},
        "workflow_candidates": {"type": "array", "items": {"type": "string"}},
        "structural_terms": {"type": "array", "items": {"type": "string"}},
        "constraints": {"type": "array", "items": {"type": "string"}},
        "version_specific_facts": {"type": "array", "items": {"type": "string"}},
        "evidence_index": {"type": "array", "items": EVIDENCE_REF},
    },
    "required": ["domain_purpose", "capability_candidates", "workflow_candidates"],
    "additionalProperties": True,
}

GOALS_SCHEMA: dict[str, Any] = {
    "title": "H30GoalExtraction",
    "type": "object",
    "properties": {
        "goals": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "key": {"type": "string"},
                    "title": {"type": "string"},
                    "outcome": {"type": "string"},
                    "why_it_matters": {"type": "string"},
                    "prerequisite_goal_keys": {"type": "array", "items": {"type": "string"}},
                    "evidence_refs": {"type": "array", "items": EVIDENCE_REF},
                },
                "required": ["key", "title", "outcome"],
                "additionalProperties": True,
            },
        }
    },
    "required": ["goals"],
    "additionalProperties": True,
}

PROCESSES_SCHEMA: dict[str, Any] = {
    "title": "H40MainProcessConstruction",
    "type": "object",
    "properties": {
        "key": {"type": "string"},
        "title": {"type": "string"},
        "outcome": {"type": "string"},
        "stages": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "key": {"type": "string"},
                    "title": {"type": "string"},
                    "local_outcome": {"type": "string"},
                },
                "required": ["key", "title", "local_outcome"],
                "additionalProperties": True,
            },
        },
    },
    "required": ["key", "title", "outcome", "stages"],
    "additionalProperties": True,
}

STAGES_SCHEMA: dict[str, Any] = {
    "title": "H50StageEnrichment",
    "type": "object",
    "properties": {
        "stages": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "key": {"type": "string"},
                    "title": {"type": "string"},
                    "local_goal": {"type": "string"},
                    "why_it_exists": {"type": "string"},
                    "local_outcome": {"type": "string"},
                    "dependency_notes": {"type": "array", "items": {"type": "string"}},
                    "concept_candidates": {"type": "array", "items": {"type": "string"}},
                    "operation_candidates": {"type": "array", "items": {"type": "string"}},
                    "implementation_detail_candidates": {
                        "type": "array",
                        "items": {"type": "object"},
                    },
                    "example_candidate": {"type": "object"},
                    "evidence_refs": {"type": "array", "items": EVIDENCE_REF},
                },
                "required": ["key", "local_goal", "local_outcome"],
                "additionalProperties": True,
            },
        }
    },
    "required": ["stages"],
    "additionalProperties": True,
}

CANONICALIZE_SCHEMA: dict[str, Any] = {
    "title": "H60CanonicalizeConceptsOperations",
    "type": "object",
    "properties": {
        "concepts": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "key": {"type": "string"},
                    "name": {"type": "string"},
                    "definition": {"type": "string"},
                    "role": {"type": "string"},
                    "related_concept_keys": {"type": "array", "items": {"type": "string"}},
                    "key_operation_keys": {"type": "array", "items": {"type": "string"}},
                },
                "required": ["key", "name", "definition", "role"],
                "additionalProperties": True,
            },
        },
        "operations": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "key": {"type": "string"},
                    "name": {"type": "string"},
                    "definition": {"type": "string"},
                    "purpose": {"type": "string"},
                    "acts_on_concept_keys": {"type": "array", "items": {"type": "string"}},
                    "common_failures": {"type": "array", "items": {"type": "string"}},
                },
                "required": ["key", "name", "definition"],
                "additionalProperties": True,
            },
        },
        "stage_bindings": {
            "type": "object",
            "description": "Maps stage key to the concept/operation keys it uses.",
            "additionalProperties": {
                "type": "object",
                "properties": {
                    "concept_keys": {"type": "array", "items": {"type": "string"}},
                    "operation_keys": {"type": "array", "items": {"type": "string"}},
                },
                "additionalProperties": True,
            },
        },
    },
    "required": ["concepts", "operations", "stage_bindings"],
    "additionalProperties": True,
}

COMPRESSION_SCHEMA: dict[str, Any] = {
    "title": "H70BranchFoundationCompression",
    "type": "object",
    "properties": {
        "alternative_branches": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "key": {"type": "string"},
                    "title": {"type": "string"},
                    "description": {"type": "string"},
                    "parent_stage_key": {"type": "string"},
                },
                "required": ["key", "title", "parent_stage_key"],
                "additionalProperties": True,
            },
        },
        "extension_branches": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "key": {"type": "string"},
                    "title": {"type": "string"},
                    "description": {"type": "string"},
                    "parent_process_key": {"type": "string"},
                },
                "required": ["key", "title", "parent_process_key"],
                "additionalProperties": True,
            },
        },
    },
    "required": ["alternative_branches", "extension_branches"],
    "additionalProperties": True,
}

LEARNING_LAYER_SCHEMA: dict[str, Any] = {
    "title": "H80LearningLayer",
    "type": "object",
    "properties": {
        "mental_model": {
            "type": "object",
            "properties": {
                "summary": {"type": "string"},
                "flow": {"type": "array", "items": {"type": "string"}},
            },
            "required": ["summary"],
            "additionalProperties": True,
        },
        "practices": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "key": {"type": "string"},
                    "title": {"type": "string"},
                    "process_key": {"type": "string"},
                    "instructions": {"type": "array", "items": {"type": "string"}},
                    "expected_outcome": {"type": "string"},
                    "checkpoint_questions": {"type": "array", "items": {"type": "string"}},
                },
                "required": ["key", "title", "process_key", "instructions", "expected_outcome"],
                "additionalProperties": True,
            },
        },
        "expansion_map": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "title": {"type": "string"},
                    "description": {"type": "string"},
                    "from_goal_key": {"type": "string"},
                },
                "required": ["title"],
                "additionalProperties": True,
            },
        },
    },
    "required": ["mental_model", "practices", "expansion_map"],
    "additionalProperties": True,
}

CRITIC_SCHEMA: dict[str, Any] = {
    "title": "H100Critic",
    "type": "object",
    "properties": {
        "severity": {"type": "string", "enum": ["pass", "minor", "major"]},
        "issues": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "code": {"type": "string"},
                    "entity_ref": {"type": "string"},
                    "explanation": {"type": "string"},
                    "recommended_change": {"type": "string"},
                },
                "required": ["code", "entity_ref", "explanation", "recommended_change"],
                "additionalProperties": True,
            },
        },
    },
    "required": ["severity", "issues"],
    "additionalProperties": True,
}

REFINE_SCHEMA: dict[str, Any] = {
    "title": "H110Refine",
    "type": "object",
    "properties": {
        "revisions": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "entity_type": {
                        "type": "string",
                        "enum": ["goal", "process", "stage", "concept", "operation", "branch"],
                    },
                    "entity_key": {"type": "string"},
                    "field": {"type": "string"},
                    "value": {"type": "string"},
                },
                "required": ["entity_type", "entity_key", "field", "value"],
                "additionalProperties": True,
            },
        }
    },
    "required": ["revisions"],
    "additionalProperties": True,
}

CRITIC_ISSUE_CODES = (
    "GOAL_TOO_VAGUE",
    "PROCESS_MAINLINE_HIDDEN",
    "STAGE_TOO_BROAD",
    "CONCEPT_OVERPROMOTED",
    "OPERATION_TOO_LOW_LEVEL",
    "ENCYCLOPEDIA_DRIFT",
    "API_MANUAL_DRIFT",
    "OVERSIMPLIFIED",
    "MISSING_CORE_CONCEPT",
    "WEAK_PRACTICE",
    "UNSUPPORTED_SPECIFIC_CLAIM",
    # Synthesised by H140 when the critic found nothing for the targeted entity.
    # Without it the mock would have no recognised issue to act on and a
    # refinement would silently propose nothing.
    "USER_REQUESTED_REFINEMENT",
)

# H120 asks for the whole artifact back, so the schema stays deliberately loose:
# the point of the step is to fix reported reference errors, and a strict schema
# would fail the response for reasons the repair prompt never asked about.
ARTIFACT_REPAIR_SCHEMA: dict[str, Any] = {
    "title": "H120RepairArtifact",
    "type": "object",
    "required": [
        "schema_version",
        "artifact_id",
        "domain",
        "mental_model",
        "goals",
        "shared_foundations",
        "main_processes",
        "stages",
        "concepts",
        "operations",
        "branches",
        "practices",
        "expansion_map",
        "metadata",
    ],
    "additionalProperties": True,
}

# Fields a refiner may rewrite. Anything else is structural and stays code-owned.
REFINABLE_FIELDS: dict[str, frozenset[str]] = {
    "goal": frozenset({"title", "outcome", "why_it_matters"}),
    "process": frozenset({"title", "outcome"}),
    "stage": frozenset({"title", "local_goal", "why_it_exists", "local_outcome", "example"}),
    "concept": frozenset({"name", "definition", "role"}),
    "operation": frozenset({"name", "definition", "purpose"}),
    "branch": frozenset({"title", "description"}),
}
