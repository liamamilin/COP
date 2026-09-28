import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from app.domain.cop_models import COPArtifact

ROOT = Path(__file__).resolve().parents[2]
FIXTURE = ROOT / "fixtures" / "reference-langchain-cop.json"


def load_fixture() -> dict:
    with FIXTURE.open(encoding="utf-8") as handle:
        return json.load(handle)


def test_reference_artifact_is_valid() -> None:
    artifact = COPArtifact.model_validate(load_fixture())
    assert artifact.domain.name == "LangChain Agent Development"
    assert len(artifact.main_processes) == 5


def test_broken_reference_is_rejected() -> None:
    data = load_fixture()
    data["main_processes"][0]["stage_refs"][0] = "stage.missing"
    with pytest.raises(ValidationError, match="missing stage"):
        COPArtifact.model_validate(data)
