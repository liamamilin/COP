#!/usr/bin/env python3
"""Verify the packaged reference artifact against the canonical schema.

The repo ships two copies of the LangChain reference COP: one under
`fixtures/` used by the seed script and tests, and one inside the frozen spec
package. They must stay identical, or the artifact a user gets from `make seed`
would differ from the one the specification declares as the quality reference.

Run from `backend/`:  uv run python ../scripts/check_reference_artifact.py
"""

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "backend"))

from app.domain.cop_models import COPArtifact  # noqa: E402
from app.domain.validation import validate_artifact  # noqa: E402

CANONICAL_SCHEMA = REPO_ROOT / "schemas" / "cop-artifact.schema.json"
SEED_FIXTURE = REPO_ROOT / "fixtures" / "reference-langchain-cop.json"
PACKAGED_REFERENCE = (
    REPO_ROOT
    / "cop-studio-development-spec-v1.0"
    / "examples"
    / "reference-langchain"
    / "reference-langchain-cop.json"
)

# The spec records these counts in VALIDATION_REPORT.json.
EXPECTED_COUNTS = {
    "goals": 5,
    "shared_foundations": 1,
    "main_processes": 5,
    "stages": 22,
    "concepts": 16,
    "operations": 12,
    "branches": 6,
    "practices": 5,
}


def fail(message: str) -> None:
    print(f"error: {message}", file=sys.stderr)
    raise SystemExit(1)


def main() -> None:
    for path in (CANONICAL_SCHEMA, SEED_FIXTURE, PACKAGED_REFERENCE):
        if not path.exists():
            fail(f"missing required file: {path.relative_to(REPO_ROOT)}")

    seed_raw = SEED_FIXTURE.read_bytes()
    packaged_raw = PACKAGED_REFERENCE.read_bytes()
    if seed_raw != packaged_raw:
        fail(
            "the seed fixture and the packaged reference artifact have drifted; "
            f"{SEED_FIXTURE.relative_to(REPO_ROOT)} must match "
            f"{PACKAGED_REFERENCE.relative_to(REPO_ROOT)}"
        )

    artifact = validate_artifact(json.loads(seed_raw), CANONICAL_SCHEMA)
    counts = {
        "goals": len(artifact.goals),
        "shared_foundations": len(artifact.shared_foundations),
        "main_processes": len(artifact.main_processes),
        "stages": len(artifact.stages),
        "concepts": len(artifact.concepts),
        "operations": len(artifact.operations),
        "branches": len(artifact.branches),
        "practices": len(artifact.practices),
    }
    if counts != EXPECTED_COUNTS:
        fail(f"reference artifact counts changed: expected {EXPECTED_COUNTS}, found {counts}")

    # The packaged schema must also accept the artifact through the Pydantic
    # export alone, so both consumers of the schema stay in agreement.
    COPArtifact.model_validate(json.loads(seed_raw))

    print("reference artifact OK:", ", ".join(f"{k}={v}" for k, v in counts.items()))


if __name__ == "__main__":
    main()
