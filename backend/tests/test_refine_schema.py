"""Refinement contracts through the same validation boundary used by live models."""

import copy
import json

import httpx
import pytest
from jsonschema import Draft202012Validator

from app.harness.context import HarnessContext
from app.harness.prompts import build_refine_prompt
from app.harness.providers import MockProvider, OpenAICompatibleProvider, ProviderError
from app.harness.runner import RunStore, run_pipeline
from app.harness.schemas import (
    EXAMPLE_SCHEMA,
    IMPLEMENTATION_DETAIL_SCHEMA,
    REFINABLE_FIELDS,
    REFINE_SCHEMA,
    STRUCTURED_REVISION_SCHEMAS,
    TEXT_REFINE_SCHEMA,
)
from app.harness.steps.h110_refine import apply_revisions

DETAILS = [{"title": "Install", "command": "pip install example", "expected_result": "Installed"}]
EXAMPLE = {"summary": "A successful run", "input": "request", "output": "response"}


def revision(kind="stage", field="example", value=None):
    return {
        "entity_type": kind,
        "entity_key": f"{kind}.a",
        "field": field,
        "value": EXAMPLE if value is None else value,
    }


@pytest.mark.parametrize(
    "kind,field,value",
    [
        (
            kind,
            field,
            STRUCTURED_REVISION_SCHEMAS.get(kind, {}).get(field)
            and {
                "example": EXAMPLE,
                "implementation_details": DETAILS,
                "common_failures": ["Missing credentials"],
            }[field]
            or "Updated text",
        )
        for kind, fields in REFINABLE_FIELDS.items()
        for field in sorted(fields)
    ],
)
def test_every_refinable_field_accepts_its_declared_shape(kind, field, value):
    Draft202012Validator(REFINE_SCHEMA).validate({"revisions": [revision(kind, field, value)]})


@pytest.mark.parametrize(
    "item",
    [
        revision("goal", "title", EXAMPLE),
        revision("stage", "example", "not an object"),
        revision("stage", "example", {"input": "missing summary"}),
        revision("stage", "example", {"summary": ["wrong type"]}),
        revision("stage", "implementation_details", "not a list"),
        revision("stage", "implementation_details", [{"command": "missing title"}]),
        revision("stage", "implementation_details", []),
        revision("operation", "common_failures", [{"text": "not a string"}]),
        revision("operation", "common_failures", []),
        revision("goal", "example", EXAMPLE),
        revision("stage", "stage_refs", ["stage.other"]),
        revision("stage", "id", "stage.hijacked"),
        revision("goal", "title", ""),
    ],
)
def test_wrong_shapes_and_structural_fields_are_not_loosened(item):
    assert not Draft202012Validator(REFINE_SCHEMA).is_valid({"revisions": [item]})


def test_generation_and_refinement_reuse_the_same_structured_shapes():
    assert STRUCTURED_REVISION_SCHEMAS["stage"]["example"] is EXAMPLE_SCHEMA
    assert (
        STRUCTURED_REVISION_SCHEMAS["stage"]["implementation_details"]["items"]
        is IMPLEMENTATION_DETAIL_SCHEMA
    )
    Draft202012Validator.check_schema(REFINE_SCHEMA)
    Draft202012Validator.check_schema(TEXT_REFINE_SCHEMA)


def test_targeted_review_keeps_its_text_only_contract():
    validator = Draft202012Validator(TEXT_REFINE_SCHEMA)
    assert validator.is_valid({"revisions": [revision("goal", "title", "Better title")]})
    assert not validator.is_valid({"revisions": [revision()]})
    system, _ = build_refine_prompt(
        artifact={}, issues=[], locked_paths=[], language="en", structured_values=False
    )
    assert "plain text fields only" in system
    assert "Structured fields use their own value shapes" not in system


def test_direct_applier_rejects_malformed_objects_without_touching_original():
    original = {
        "stages": [{"id": "stage.a", "example": EXAMPLE, "implementation_details": DETAILS}]
    }
    updated, applied, rejected = apply_revisions(
        original, [revision(value={"input": "no summary"})], []
    )
    assert updated == original
    assert not applied
    assert rejected[0]["reason"] == "replacement value has an invalid shape"
    _, applied, rejected = apply_revisions(original, [revision()], ["stage.a.example"])
    assert not applied
    assert rejected[0]["reason"] == "path is locked by user edits"


class MemoryStore(RunStore):
    def __init__(self):
        self.events = []

    def emit(self, run_id, events):
        self.events.extend(events)

    def save_checkpoint(self, run_id, context):
        pass

    def heartbeat(self, run_id):
        pass

    def metrics(self, run_id):
        return {}

    def is_cancelled(self, run_id):
        return False

    def set_candidate(self, run_id, artifact):
        pass


@pytest.mark.asyncio
async def test_structured_refinements_pass_the_real_adapter_and_resume_from_h110():
    context = HarnessContext(
        run_id="test-run",
        project_id="test-project",
        input={"topic": "Read CSV"},
        settings={"language": "en", "generation_depth": "fast"},
    )
    generated = await run_pipeline(context, MockProvider(), MemoryStore())
    assert generated.status == "completed"
    context = HarnessContext.from_dict(copy.deepcopy(context.to_dict()))
    # Restore a checkpoint immediately before H110, just like the failed live run.
    context.completed_steps = context.completed_steps[: context.completed_steps.index("H110")]
    context.critic_report = {"severity": "major", "issues": []}
    stage = context.artifact["stages"][0]
    operation = context.artifact["operations"][0]
    expected_example = copy.deepcopy(stage["example"])
    expected_details = copy.deepcopy(stage["implementation_details"])
    expected_failures = copy.deepcopy(operation["common_failures"])
    revisions = [
        {**revision(field="example", value=expected_example), "entity_key": stage["id"]},
        {
            **revision(field="implementation_details", value=expected_details),
            "entity_key": stage["id"],
        },
        {
            **revision("operation", "common_failures", expected_failures),
            "entity_key": operation["id"],
        },
    ]
    stage["example"] = None
    stage["implementation_details"] = []
    operation["common_failures"] = []
    requests = []

    def handler(request: httpx.Request):
        body = json.loads(request.content)
        requests.append(body)
        assert request.url.path == "/v1/chat/completions"
        assert "H110Refine" in body["messages"][0]["content"]
        return httpx.Response(
            200,
            json={
                "choices": [
                    {
                        "message": {
                            "content": json.dumps({"revisions": revisions}),
                        }
                    }
                ]
            },
        )

    provider = OpenAICompatibleProvider(
        base_url="https://provider.test/v1",
        api_key="fake-key",
        model="fake-model",
        transport=httpx.MockTransport(handler),
    )
    store = MemoryStore()
    outcome = await run_pipeline(context, provider, store)
    assert outcome.status == "completed", outcome.error_message
    assert len(requests) == 1, "validation must not need another model request"
    starts = [e.payload["step"] for e in store.events if e.event_type == "step.started"]
    assert starts == ["H110", "H120", "H130"]
    assert context.artifact["stages"][0]["example"] == expected_example
    assert context.artifact["stages"][0]["implementation_details"] == expected_details
    assert context.artifact["operations"][0]["common_failures"] == expected_failures


@pytest.mark.asyncio
async def test_live_adapter_still_rejects_an_object_for_a_text_field():
    def handler(request):
        return httpx.Response(
            200,
            json={
                "choices": [
                    {
                        "message": {
                            "content": json.dumps(
                                {"revisions": [revision("goal", "title", EXAMPLE)]}
                            ),
                        }
                    }
                ]
            },
        )

    provider = OpenAICompatibleProvider(
        base_url="https://provider.test/v1",
        api_key="fake-key",
        model="fake-model",
        transport=httpx.MockTransport(handler),
    )
    with pytest.raises(ProviderError) as error:
        await provider.generate_structured(
            system_prompt="Refine", user_prompt="Fix title", schema=REFINE_SCHEMA
        )
    assert error.value.code == "PROVIDER_INVALID_OUTPUT"
