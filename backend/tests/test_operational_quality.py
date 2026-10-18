"""R0 — operational completeness, and the failing baseline it records.

Three layers, deliberately separate:

    L1 structural   valid COP, every reference resolves
    L2 operational  a reader can act: examples, implementation details,
                    setup commands, a way to verify success
    L3 learnable    practices, checkpoints, somewhere to go next

`test_artifact_validation.py` already covers L1 through the JSON Schema. These
tests exist because passing L1 was repeatedly mistaken for the product
working: the reference LangChain artifact has been schema-valid the whole time
while telling a reader nothing they could execute.

The tests marked `xfail(strict=True)` are the R0 deliverable proper. They fail
today and are expected to keep failing until the batch named in the reason
lands. `strict=True` is the important part: if a batch fixes the gap, the
xfail turns into an XPASS, which pytest reports as a FAILURE, so the test
cannot quietly rot into an assumption. Promote it by deleting the marker.
"""

import json
from collections import Counter
from pathlib import Path
from typing import Any

import pytest

from app.domain.quality import (
    DUPLICATE_ENTITY_ID,
    L2,
    L3,
    MISSING_IMPLEMENTATION_DETAIL,
    MISSING_STAGE_EXAMPLE,
    OPERATION_WITHOUT_COMMON_FAILURES,
    ORPHAN_EVIDENCE_REF,
    check_artifact,
    completeness_summary,
)

FIXTURE_PATH = Path(__file__).resolve().parents[2] / "fixtures" / "reference-langchain-cop.json"


@pytest.fixture(scope="module")
def reference() -> dict[str, Any]:
    with FIXTURE_PATH.open(encoding="utf-8") as handle:
        return json.load(handle)


@pytest.fixture(scope="module")
def reference_source_ids() -> set[str]:
    """The sources a project seeded from this fixture would actually have."""
    with FIXTURE_PATH.open(encoding="utf-8") as handle:
        artifact = json.load(handle)
    return set((artifact.get("metadata") or {}).get("source_ids") or [])


def _codes(issues) -> Counter:
    return Counter(issue.code for issue in issues)


# --------------------------------------------------------------------------
# The checker itself. These are the contract every later batch depends on.
# --------------------------------------------------------------------------


def test_a_duplicate_entity_id_is_reported() -> None:
    """Two entities sharing an id makes every reference to it ambiguous."""
    duplicates = {
        "goals": [
            {"id": "g", "title": "One", "outcome": "a"},
            {"id": "g", "title": "Two", "outcome": "b"},
        ],
        "stages": [],
    }

    issues = [i for i in check_artifact(duplicates) if i.code == DUPLICATE_ENTITY_ID]

    assert len(issues) == 1
    assert issues[0].entity_ref == "g"
    assert issues[0].entity_type == "goal"


def test_an_entity_without_an_id_is_reported() -> None:
    issues = [
        i for i in check_artifact({"stages": [{"title": "No id"}]}) if i.code == DUPLICATE_ENTITY_ID
    ]

    assert len(issues) == 1
    assert issues[0].entity_type == "stage"


def test_a_dangling_reference_is_reported_with_both_ends(reference) -> None:
    artifact = json.loads(json.dumps(reference))
    artifact["stages"][0]["concept_refs"] = ["concept.does-not-exist"]
    artifact["stages"][0]["implementation_details"] = [{"title": "t", "action": "a"}]
    artifact["stages"][0]["example"] = {"summary": "s"}
    artifact["operations"][0]["common_failures"] = ["boom"]

    issues = [i for i in check_artifact(artifact) if i.code == "DANGLING_REF"]

    assert len(issues) == 1
    assert issues[0].entity_ref == artifact["stages"][0]["id"]
    # The message has to name the missing id, or it is unactionable.
    assert "concept.does-not-exist" in issues[0].explanation


def test_orphan_detection_is_skipped_when_sources_are_unknown(reference) -> None:
    """A caller that does not know the sources must not be told all refs are broken."""
    without = [i for i in check_artifact(reference) if i.code == ORPHAN_EVIDENCE_REF]
    with_empty = [
        i
        for i in check_artifact(reference, known_source_ids=set())
        if i.code == ORPHAN_EVIDENCE_REF
    ]

    assert without == []
    assert with_empty, "an explicit empty source set must report every reference as an orphan"


def test_empty_requirements_do_not_count_as_coverage_failures() -> None:
    """A COP with no Operations has nothing to cover; that is not a defect."""
    summary = completeness_summary({"stages": [{"id": "s", "title": "Read"}], "operations": []})

    assert summary["coverage"]["implementation_detail"] == 1.0
    assert summary["coverage"]["operation_common_failures"] == 1.0


def test_setup_stages_are_recognised_in_both_english_and_chinese() -> None:
    from app.domain.quality import is_setup_stage

    assert is_setup_stage({"title": "Install LangChain"})
    assert is_setup_stage({"title": "配置模型 Provider"})
    assert not is_setup_stage({"title": "Inspect the resulting message"})


def test_reading_only_stages_are_not_demanded_an_implementation_detail() -> None:
    """A Stage with Concepts but no Operations is reading, not doing."""
    artifact = {
        "concepts": [{"id": "c", "name": "Harness", "definition": "d", "role": "r"}],
        "stages": [
            {
                "id": "stage.read",
                "title": "Understand the harness",
                "concept_refs": ["c"],
                "operation_refs": [],
                "example": {"summary": "an example"},
            }
        ],
    }

    # Scoped to L2: this bare fixture has no practices and no expansion map,
    # which is an L3 matter and not what this test is about.
    assert [i.code for i in check_artifact(artifact, levels=[L2])] == []


def test_duplicate_ids_are_reported_because_refs_become_ambiguous() -> None:
    artifact = {
        "stages": [
            {"id": "s", "title": "One", "operation_refs": [], "example": {"summary": "a"}},
            {"id": "s", "title": "Two", "operation_refs": [], "example": {"summary": "b"}},
        ]
    }

    issues = [i for i in check_artifact(artifact) if i.code == "DUPLICATE_ENTITY_ID"]

    assert len(issues) == 1
    assert issues[0].entity_ref == "s"


# --------------------------------------------------------------------------
# The shipped seed fixture.
#
# These are the R7 gate, not the R1 one. R1 makes the *generator* produce
# compliant artifacts and is asserted in `test_content_contract.py`; the LangChain
# reference artifact checked into the repository is rebuilt with real content in
# R7. Keeping the two apart matters: fixing generation and fixing the seed are
# different changes, and one green does not imply the other.
# --------------------------------------------------------------------------


def test_the_baseline_numbers_are_what_the_audit_recorded(reference, reference_source_ids) -> None:
    """Pin the R0 measurement so a later batch's improvement is visible as a delta."""
    summary = completeness_summary(reference, known_source_ids=reference_source_ids)

    assert summary["counts"]["stages"] == 22
    assert summary["counts"]["executable_stages"] == 22
    assert summary["counts"]["practices"] == 5
    # The structure is sound. Nothing here is a reference-integrity problem.
    assert summary["levels"]["L1"]["clean"] or summary["orphan_evidence_refs"] > 0


def test_the_shipped_fixture_is_operationally_complete(reference, reference_source_ids) -> None:
    """R7. 22 Stages, every one of which a reader could act on.

    The failure names the exact counts, so the message is the progress report:
    how many Stages still lack an example, an implementation detail, a failure
    mode, or all three.
    """
    summary = completeness_summary(reference, known_source_ids=reference_source_ids)
    counts = summary["counts"]

    def missing(have: int, total: int) -> str:
        return f"{total - have} of {total} still missing"

    assert summary["coverage"]["stage_example"] == 1.0, (
        "R7: every Stage needs an example; "
        f"{missing(counts['stages_with_example'], counts['stages'])}"
    )
    assert summary["coverage"]["implementation_detail"] == 1.0, (
        "R7: every executable Stage needs an implementation detail; "
        f"{missing(counts['executable_stages_with_detail'], counts['executable_stages'])}"
    )
    assert summary["coverage"]["operation_common_failures"] == 1.0, (
        "R7: every Operation needs a common failure; "
        f"{missing(counts['operations_with_common_failures'], counts['operations'])}"
    )


@pytest.mark.parametrize(
    "code, level, reason",
    [
        (MISSING_STAGE_EXAMPLE, L2, "R7 seed fixture"),
        (MISSING_IMPLEMENTATION_DETAIL, L2, "R7 seed fixture"),
        (OPERATION_WITHOUT_COMMON_FAILURES, L2, "R7 seed fixture"),
    ],
)
def test_no_level_two_gap_survives_in_the_shipped_fixture(reference, code, level, reason) -> None:
    """R7 per-code gate over the seed artifact. Names the failing entity."""
    issues = [i for i in check_artifact(reference) if i.code == code and i.level == level]
    assert issues == [], (
        reason + ": " + "; ".join(f"{i.entity_ref} ({i.explanation})" for i in issues[:5])
    )


def test_install_langchain_stage_is_actionable_and_verifiable(reference) -> None:
    """R7. The plan names this Stage: it is where a beginner stops.

    Install is the Stage a reader reaches first, and a first Stage that gives no
    command and no way to check success ends the session there.
    """
    stages = {s["id"]: s for s in reference["stages"]}
    install = stages.get("stage.foundation.install")
    assert install is not None, "the reference fixture must keep an install Stage"

    details = install.get("implementation_details") or []
    assert details, "R7: Install LangChain must carry an implementation detail"
    assert any(d.get("command") for d in details), "R7: it must carry a runnable command"
    assert any(d.get("expected_result") for d in details), "R7: it must say how to verify success"
    assert install.get("example"), "R7: it must carry an example"


def test_the_seeded_sources_match_the_fixture_citations() -> None:
    """R3/R7. A citation is only traceable if the thing it points at exists.

    The fixture ships the six sources it cites, and the seed creates a Source row
    per entry under the same id. Checking the two lists agree is what keeps a
    future fixture edit from quietly reintroducing an orphan.
    """
    sources_path = FIXTURE_PATH.with_name("reference-langchain-sources.json")
    with sources_path.open(encoding="utf-8") as handle:
        shipped = {str(item["id"]) for item in json.load(handle)}

    with FIXTURE_PATH.open(encoding="utf-8") as handle:
        artifact = json.load(handle)
    cited = {
        str(ref["source_id"])
        for collection in ("goals", "stages")
        for entity in artifact[collection]
        for ref in entity.get("evidence_refs") or []
    }

    assert cited, "the fixture is supposed to demonstrate evidence"
    assert cited <= shipped, f"cited but not shipped: {sorted(cited - shipped)}"
    assert shipped <= cited, f"shipped but never cited: {sorted(shipped - cited)}"
    assert completeness_summary(artifact, known_source_ids=shipped)["orphan_evidence_refs"] == 0


def test_evidence_anchoring_is_reported_as_a_number() -> None:
    """How checkable a COP actually is has to be measurable, not assumed.

    A citation carrying only a `source_id` says that the entity was sourced. One
    carrying a quote or a segment says what the source said, which is what lets a
    reader check the claim rather than take it on trust. Reporting the ratio is
    what makes the difference visible to a human judging a generated COP; a
    boolean "it has evidence" hides it completely.
    """

    def summary_for(refs: list[dict]) -> dict:
        return completeness_summary({"stages": [{"id": "s", "evidence_refs": refs}]})

    only_ids = summary_for([{"source_id": "a"}, {"source_id": "b"}])
    assert only_ids["evidence"] == {
        "refs": 2,
        "refs_without_an_anchor": 2,
        "refs_without_a_quote": 2,
    }
    assert only_ids["coverage"]["evidence_anchored"] == 0.0

    mixed = summary_for(
        [{"source_id": "a", "quote_hint": "create_agent is the entry point."}, {"source_id": "b"}]
    )
    assert mixed["evidence"]["refs_without_a_quote"] == 1
    assert mixed["coverage"]["evidence_anchored"] == 0.5

    # A segment anchor counts for `anchored` but not for a quote: it says where in
    # the source, not what the source said. Reporting only one of the two would
    # hide that difference.
    segmented = summary_for([{"source_id": "a", "segment_id": "overview-create-agent"}])
    assert segmented["coverage"]["evidence_anchored"] == 1.0
    assert segmented["evidence"]["refs_without_a_quote"] == 1, (
        "a segment is not a quote; the reader still has to go and find the text"
    )

    # No evidence at all is a coverage question, not a failure: nothing to anchor.
    assert summary_for([])["coverage"]["evidence_anchored"] == 1.0


def test_the_shipped_fixture_reports_how_anchored_its_citations_are(
    reference, reference_source_ids
) -> None:
    """Pins the numbers, so the figures in DEVELOPMENT_PLAN are checkable.

    Every ref resolves, which was the R3 gate. This is the weaker question behind
    it: does each citation also narrow down *where* and *what* the source said.
    """
    summary = completeness_summary(reference, known_source_ids=reference_source_ids)

    assert summary["evidence"] == {
        # 15 citations across Goals and Stages.
        "refs": 15,
        # Every one names a segment, so the reader is told where to look.
        "refs_without_an_anchor": 0,
        # None carries the text it is relying on, so the reader has to go and
        # find it. This is the open evidence-quality question.
        "refs_without_a_quote": 15,
    }


def test_learnable_layer_passes_for_the_reference_artifact(reference) -> None:
    """L3 is already satisfied; recording that stops a later batch regressing it."""
    assert check_artifact(reference, levels=[L3]) == []


def test_a_fully_actionable_artifact_is_clean_at_l2() -> None:
    """The positive control. Without it, 'no issues' proves nothing."""
    artifact = {
        "stages": [
            {
                "id": "stage.install",
                "title": "Install the package",
                "local_goal": "Get a working environment",
                "concept_refs": [],
                "operation_refs": ["op.install"],
                "example": {"summary": "pip install reports success"},
                "implementation_details": [
                    {
                        "title": "Install into a virtual environment",
                        "action": "Create an environment and install the package",
                        "command": "python -m venv .venv && .venv/bin/pip install pkg",
                        "expected_result": "pip prints 'Successfully installed pkg'",
                        "caution": "Never install into the system interpreter",
                    }
                ],
            }
        ],
        "operations": [
            {
                "id": "op.install",
                "name": "Install the package",
                "definition": "d",
                "common_failures": ["no venv"],
            }
        ],
    }

    assert check_artifact(artifact, levels=[L2]) == []


def test_issue_codes_are_stable() -> None:
    """These strings cross module boundaries; renaming one silently breaks callers."""
    from app.domain import quality

    expected = {
        "DANGLING_REF",
        "ORPHAN_EVIDENCE_REF",
        "MISSING_STAGE_EXAMPLE",
        "MISSING_IMPLEMENTATION_DETAIL",
        "IMPLEMENTATION_DETAIL_NOT_ACTIONABLE",
        "SETUP_NOT_ACTIONABLE",
        "MISSING_VALIDATION_STEP",
        "OPERATION_WITHOUT_COMMON_FAILURES",
        "WEAK_PRACTICE",
        "PRACTICE_WITHOUT_CHECKPOINT",
        "EMPTY_EXPANSION_MAP",
    }
    declared = {
        value
        for name, value in vars(quality).items()
        if name.isupper() and isinstance(value, str) and value.isupper() and "_" in value
    }

    assert expected <= declared, f"missing codes: {sorted(expected - declared)}"


def test_summary_counts_every_stage_separately_from_executable_ones() -> None:
    artifact = {
        "stages": [
            {"id": "a", "title": "Do", "operation_refs": ["x"], "example": {"summary": "s"}},
            {"id": "b", "title": "Read", "operation_refs": [], "example": {"summary": "s"}},
        ]
    }
    summary = completeness_summary(artifact)

    assert summary["counts"]["stages"] == 2
    assert summary["counts"]["executable_stages"] == 1
