"""Generated experimental contracts remain independent and reproducible."""

import importlib.util
import json
from pathlib import Path

from jsonschema import Draft202012Validator

from app.domain.learning_unit import LearningUnit, check_learning_unit, unit_manifest

ROOT = Path(__file__).resolve().parents[2]


def load(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def generator():
    spec = importlib.util.spec_from_file_location(
        "generate_types",
        ROOT / "scripts/generate-types.py",
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_experimental_schema_is_generated_from_the_model_and_fixture_is_valid():
    schema = load("schemas/learning-unit.experimental.schema.json")
    for key, value in LearningUnit.model_json_schema().items():
        assert schema[key] == value
    Draft202012Validator.check_schema(schema)
    raw = load("fixtures/langchain-basic-learning-unit.json")
    Draft202012Validator(schema).validate(raw)
    # Optional experimental explanations must not rewrite old saved documents.
    assert LearningUnit.model_validate(raw).model_dump(mode="json", exclude_unset=True) == raw


def test_generated_types_and_original_cop_types_have_no_drift():
    module = generator()
    source = "schemas/learning-unit.experimental.schema.json"
    expected = module.generate_document(load(source), "LearningUnit", source)
    assert (ROOT / "packages/cop-types/generated/learning-unit.ts").read_text() == expected
    assert "content_ref: DetailRef | null" in expected
    assert ": unknown" not in expected
    original = module.generate(load("schemas/cop-artifact.schema.json"))
    assert (ROOT / "packages/cop-types/generated/index.ts").read_text() == original


def test_authored_unit_and_separate_manifest_are_current_and_not_execution_claims():
    raw = load("fixtures/langchain-basic-learning-unit.json")
    artifact = load("fixtures/langchain-basic-cop.json")
    assert check_learning_unit(raw, artifact) == []
    manifest = load("fixtures/langchain-basic-learning-unit.manifest.json")
    assert manifest == unit_manifest(raw, artifact)
    assert manifest["scope"] == "structure-and-bindings-only"
    assert "learner understanding" in manifest["not_verified"]
    assert "automatic generation stability" in manifest["not_verified"]
