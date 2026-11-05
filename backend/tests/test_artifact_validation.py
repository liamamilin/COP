import importlib.util
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


def test_reference_regeneration_updates_both_copies(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A future enrichment must not drop operational content from the package."""
    spec = importlib.util.spec_from_file_location(
        "enrich_langchain_fixture", ROOT / "backend/scripts/enrich_langchain_fixture.py"
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    seed = tmp_path / "seed.json"
    packaged = tmp_path / "packaged.json"
    seed.write_bytes(FIXTURE.read_bytes())
    packaged.write_text("{}\n", encoding="utf-8")
    monkeypatch.setattr(module, "FIXTURE", seed)
    monkeypatch.setattr(module, "PACKAGED_REFERENCE", packaged)
    monkeypatch.setattr(module, "SOURCES_OUT", tmp_path / "sources.json")

    module.main()

    assert seed.read_bytes() == packaged.read_bytes()
    artifact = COPArtifact.model_validate_json(packaged.read_text(encoding="utf-8"))
    assert len(artifact.stages) == 22
    assert all(stage.example and stage.implementation_details for stage in artifact.stages)
    assert all(operation.common_failures for operation in artifact.operations)
    before = seed.read_bytes()
    module.main()
    assert seed.read_bytes() == packaged.read_bytes() == before
