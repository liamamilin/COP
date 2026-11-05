"""Bounded fan-out and multi-batch canonicalization.

These tests exist because a 35-Stage run failed three times at H60 with a single
oversized request. The fix must bound request size without changing the COP
contract, so the assertions are about call shapes and merge correctness.
"""

import asyncio
from typing import Any

import pytest

from app.core.errors import HarnessError
from app.harness.batching import bounded_map, chunked
from app.harness.context import HarnessContext
from app.harness.prompts import decode_payload
from app.harness.steps.h50_stages import MAX_ENRICH_CONCURRENCY, StageEnrichmentStep
from app.harness.steps.h60_canonicalize import (
    CANONICALIZE_BATCH_SIZE,
    MAX_CANONICALIZE_BATCHES,
    CanonicalizeStep,
    canonicalization_input,
    merge_canonicalization_payloads,
)


def stage(index: int) -> dict[str, Any]:
    return {
        "key": f"s{index}",
        "title": f"Stage {index}",
        "local_goal": "Do it",
        "local_outcome": "Done",
        "concept_candidates": [f"Concept {index}"],
        "operation_candidates": [f"Operation {index}"],
    }


def test_chunking_preserves_order_and_rejects_a_zero_sized_batch():
    assert chunked([1, 2, 3, 4, 5], 2) == [[1, 2], [3, 4], [5]]
    assert chunked([], 3) == []
    with pytest.raises(ValueError):
        chunked([1], 0)


@pytest.mark.asyncio
async def test_bounded_map_never_exceeds_the_ceiling_and_keeps_input_order():
    running = 0
    peak = 0

    async def work(item: int) -> int:
        nonlocal running, peak
        running += 1
        peak = max(peak, running)
        await asyncio.sleep(0.01)
        running -= 1
        return item * 2

    result = await bounded_map(list(range(9)), work, concurrency=3)
    assert result == [item * 2 for item in range(9)]
    assert peak <= 3


def test_merging_batches_rewrites_every_reference_to_its_global_key():
    # Two batches each use the key "concept" for a different entity. A naive
    # concatenation would make the second batch's binding point at the first
    # batch's Concept, silently attaching the wrong teaching.
    notices: list[str] = []
    merged = merge_canonicalization_payloads(
        [
            {
                "concepts": [{"key": "concept", "name": "Noise", "definition": "d", "role": "r"}],
                "operations": [{"key": "op", "name": "Filter", "definition": "d"}],
                "stage_bindings": {"a": {"concept_keys": ["concept"], "operation_keys": ["op"]}},
            },
            {
                "concepts": [
                    {"key": "concept", "name": "Feedback", "definition": "d2", "role": "r2"},
                ],
                "operations": [{"key": "op", "name": "Respond", "definition": "d2"}],
                "stage_bindings": {
                    "b": {"concept_keys": ["concept"], "operation_keys": ["op"]},
                },
            },
        ],
        warnings=notices,
    )

    assert [item["name"] for item in merged["concepts"]] == ["Noise", "Feedback"]
    assert [item["name"] for item in merged["operations"]] == ["Filter", "Respond"]
    first, second = merged["concepts"]
    assert merged["stage_bindings"]["a"]["concept_keys"] == [first["key"]]
    assert merged["stage_bindings"]["b"]["concept_keys"] == [second["key"]]
    assert first["key"] != second["key"], "colliding model keys must be disambiguated"
    assert any("conflicting concepts key" in notice for notice in notices)


def test_merging_deduplicates_the_same_entity_across_batches():
    shared = {"key": "runtime", "name": "Runtime", "definition": "", "role": "r"}
    notices: list[str] = []
    merged = merge_canonicalization_payloads(
        [
            {"concepts": [shared], "operations": [], "stage_bindings": {}},
            {
                "concepts": [dict(shared, definition="The host environment")],
                "operations": [],
                "stage_bindings": {},
            },
        ],
        warnings=notices,
    )

    assert len(merged["concepts"]) == 1
    assert merged["concepts"][0]["definition"] == "The host environment"
    assert any("incomplete definition" in notice for notice in notices)


class RecordingServices:
    def __init__(self, payloads: list[dict[str, Any]]) -> None:
        self.payloads = payloads
        self.calls: list[dict[str, Any]] = []

    def is_cancelled(self) -> bool:
        return False

    async def complete_structured(self, **request: Any) -> dict[str, Any]:
        self.calls.append(request)
        return self.payloads[len(self.calls) - 1]


def canonical_context(stage_count: int) -> HarnessContext:
    stages = [stage(index) for index in range(stage_count)]
    return HarnessContext(
        run_id="r",
        project_id="p",
        settings={"language": "en"},
        process_drafts=[{"key": "p", "stages": stages}],
        stage_drafts=[{**item, "why_it_exists": "", "process_key": "p"} for item in stages],
    )


@pytest.mark.asyncio
async def test_canonicalization_splits_a_large_run_into_bounded_calls():
    count = 14
    context = canonical_context(count)
    payloads = [
        {
            "concepts": [
                {"key": f"c{index}", "name": f"Concept {index}", "definition": "d", "role": "r"}
                for index in indices
            ],
            "operations": [
                {"key": f"o{index}", "name": f"Operation {index}", "definition": "d"}
                for index in indices
            ],
            "stage_bindings": {
                f"s{index}": {"concept_keys": [f"c{index}"], "operation_keys": [f"o{index}"]}
                for index in indices
            },
        }
        for indices in chunked(list(range(count)), CANONICALIZE_BATCH_SIZE)
    ]
    services = RecordingServices(payloads)

    result = await CanonicalizeStep().execute(context, services)

    expected_calls = -(-count // CANONICALIZE_BATCH_SIZE)
    assert len(services.calls) == expected_calls
    assert all(
        len(decode_payload(call["user_prompt"])["stages"]) <= CANONICALIZE_BATCH_SIZE
        for call in services.calls
    )
    assert '"key":"c0","name":"Concept 0","definition":"d"' in services.calls[1]["user_prompt"]
    assert '"Concept 13"' in services.calls[0]["user_prompt"]
    assert result.warnings == []
    assert result.checkpoint_patch["bound_stage_keys"] == [f"s{index}" for index in range(count)]
    assert all(
        binding["concept_keys"] and binding["operation_keys"]
        for binding in result.checkpoint_patch["stage_bindings"].values()
    )


@pytest.mark.asyncio
async def test_canonicalization_refuses_an_unbounded_number_of_paid_calls():
    context = canonical_context(MAX_CANONICALIZE_BATCHES * CANONICALIZE_BATCH_SIZE + 1)
    services = RecordingServices([])

    with pytest.raises(HarnessError) as error:
        await CanonicalizeStep().execute(context, services)

    assert error.value.code == "HARNESS_TOO_MANY_STAGES"
    assert services.calls == [], "the limit must fail before spending a request"


@pytest.mark.asyncio
async def test_stage_enrichment_caps_concurrency_without_dropping_stages():
    running = 0
    peak = 0

    class Services(RecordingServices):
        async def complete_structured(self, **request: Any) -> dict[str, Any]:
            nonlocal running, peak
            running += 1
            peak = max(peak, running)
            await asyncio.sleep(0.01)
            running -= 1
            stages = decode_payload(request["user_prompt"])["stages"]
            return {
                "stages": [
                    {
                        "key": item["key"],
                        "local_goal": "g",
                        "local_outcome": "o",
                        "example_candidate": {"summary": "s"},
                        "implementation_detail_candidates": [{"title": "t", "action": "a"}],
                    }
                    for item in stages
                ]
            }

    processes = [
        {
            "key": f"p{index}",
            "goal_key": "g",
            "title": "P",
            "outcome": "O",
            "stages": [{**stage(index), "local_outcome": "x"}],
        }
        for index in range(6)
    ]
    context = HarnessContext(
        run_id="r",
        project_id="p",
        settings={"language": "en"},
        process_drafts=processes,
    )
    result = await StageEnrichmentStep().execute(context, Services([]))

    assert peak <= MAX_ENRICH_CONCURRENCY
    assert len(result.checkpoint_patch["stage_drafts"]) == 6


def test_projection_still_drops_code_bodies_before_batching():
    projected = canonicalization_input(
        [
            {
                **stage(0),
                "implementation_details": [
                    {"title": "Write", "action": "a", "command": "x" * 5000}
                ],
            }
        ]
    )[0]
    assert "command" not in str(projected)
