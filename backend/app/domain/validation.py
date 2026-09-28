import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

from app.domain.cop_models import COPArtifact


def load_json(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def validate_artifact(data: dict[str, Any], schema_path: Path | None = None) -> COPArtifact:
    if schema_path is not None:
        Draft202012Validator(load_json(schema_path)).validate(data)
    return COPArtifact.model_validate(data)
