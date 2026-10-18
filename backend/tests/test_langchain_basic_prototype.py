"""The Basic COP teaches the code that is actually executed, without a database."""

import ast
import json
import runpy
from pathlib import Path

from jsonschema import Draft202012Validator

from app.domain.cop_models import COPArtifact
from app.domain.quality import check_artifact

ROOT = Path(__file__).resolve().parents[2]
SAMPLE = ROOT / "examples/langchain-basic"
FIXTURE = ROOT / "fixtures/langchain-basic-cop.json"


def artifact() -> dict:
    return json.loads(FIXTURE.read_text(encoding="utf-8"))


def test_generated_fixture_is_current_and_does_not_touch_full_case() -> None:
    builder = runpy.run_path(str(SAMPLE / "build_cop.py"))
    assert builder["build_artifact"]() == artifact()
    sources = json.loads((ROOT / "fixtures/langchain-basic-sources.json").read_text())
    assert sources == builder["SOURCES"]
    assert builder["ARTIFACT_PATH"] != ROOT / "fixtures/reference-langchain-cop.json"


def test_basic_schema_references_quality_and_model_roundtrip() -> None:
    data = artifact()
    schema = json.loads((ROOT / "schemas/cop-artifact.schema.json").read_text())
    Draft202012Validator(schema).validate(data)
    parsed = COPArtifact.model_validate(data)
    assert parsed.main_processes[0].start.ref == parsed.shared_foundations[0].id
    assert len(parsed.stages) == 5
    assert len(parsed.goals) == 1
    assert len(parsed.branches) == 2
    assert not check_artifact(data, known_source_ids=data["metadata"]["source_ids"])
    # Existing typed/JSON storage does not drop the copyable code or practice.
    rebuilt = COPArtifact.model_validate(parsed.model_dump()).model_dump()
    assert rebuilt["stages"] == parsed.model_dump()["stages"]
    assert rebuilt["practices"] == parsed.model_dump()["practices"]


def test_every_teaching_file_equals_executed_source_and_compiles() -> None:
    details = [
        detail for stage in artifact()["stages"] for detail in stage["implementation_details"]
    ]
    for filename in (
        "requirements.txt",
        ".env.example",
        "config.py",
        "agent.py",
        "inspect_result.py",
    ):
        found = [detail for detail in details if detail["title"] == f"保存 {filename}"]
        assert len(found) == 1, filename
        assert found[0]["command"] == (SAMPLE / filename).read_text(encoding="utf-8")
        assert found[0]["action"] and found[0]["expected_result"] and found[0]["caution"]
        if filename.endswith(".py"):
            ast.parse(found[0]["command"], filename=filename)


def test_practice_traverses_same_files_input_results_and_transfer() -> None:
    data = artifact()
    text = "\n".join(data["practices"][0]["instructions"])
    for token in (
        "Foundation",
        "agent.py",
        "config.py",
        "inspect_result.py",
        "first-run.json",
        "second-run.json",
        "--message",
        "语义",
        "input",
        "密钥",
        "费用",
        "待验",
    ):
        assert token in text, token
    assert len(data["practices"][0]["checkpoint_questions"]) >= 4
    assert not any("weather" in line.lower() for line in data["practices"][0]["instructions"])


def test_branches_name_choice_change_and_rejoin_and_sources_are_not_fake_quotes() -> None:
    data = artifact()
    for branch in data["branches"]:
        assert branch["description"]
        assert "回" in branch["description"]
        parent = next(
            stage for stage in data["stages"] if stage["id"] == branch["parent_stage_ref"]
        )
        assert branch["id"] in parent["branch_refs"]
    for stage in data["stages"]:
        assert stage["example"]["note"]
        for ref in stage["evidence_refs"]:
            assert "quote_hint" not in ref  # Human summary is not a source quotation.
    assert "真实服务及目标用户验收待完成" in data["domain"]["scope"]
    assert "不是自动 Harness" in data["domain"]["non_goals"][-1]
