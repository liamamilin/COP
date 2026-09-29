"""M8 scale gates from the V1 testing strategy."""

import json
import time
from pathlib import Path

from app.db.models import COPVersion, GenerationEvent, GenerationRun, Project
from app.jobs.events import read_events

FIXTURE = Path(__file__).resolve().parents[2] / "fixtures" / "reference-langchain-cop.json"


def artifact() -> dict:
    return json.loads(FIXTURE.read_text(encoding="utf-8"))


def project(db) -> Project:
    value = Project(title="Scale", domain="Scale", scope="s")
    db.add(value)
    db.commit()
    return value


def test_version_history_handles_one_hundred_versions(client, db):
    owner = project(db)
    payload = artifact()
    db.add_all(
        COPVersion(
            project_id=owner.id,
            version_number=number,
            artifact_json=payload,
            change_summary=f"v{number}",
            created_by="harness",
        )
        for number in range(1, 101)
    )
    db.commit()

    started = time.perf_counter()
    response = client.get(f"/api/v1/projects/{owner.id}/versions")
    elapsed = time.perf_counter() - started

    assert response.status_code == 200
    assert [item["version_number"] for item in response.json()] == list(range(100, 0, -1))
    assert elapsed < 5


def test_generation_event_log_pages_through_one_thousand_events(db):
    owner = project(db)
    run = GenerationRun(project_id=owner.id, status="completed", requested_mode="standard")
    db.add(run)
    db.flush()
    db.add_all(
        GenerationEvent(
            run_id=run.id,
            sequence=number,
            event_type="step.completed",
            step="H50",
            payload_json={"number": number},
        )
        for number in range(1, 1001)
    )
    db.commit()

    first = read_events(db, run.id)
    second = read_events(db, run.id, after=first[-1].sequence)

    assert len(first) == len(second) == 500
    assert first[0].sequence == 1
    assert second[-1].sequence == 1000


def test_multi_megabyte_text_source_is_extracted(client, db):
    owner = project(db)
    text = "\n".join("A structured source line." for _ in range(120_000))

    started = time.perf_counter()
    response = client.post(
        f"/api/v1/projects/{owner.id}/sources/text",
        json={"title": "Large source", "text": text, "format": "text"},
    )
    elapsed = time.perf_counter() - started

    assert response.status_code == 201, response.text
    assert response.json()["status"] == "ready"
    assert response.json()["char_count"] == len(text)
    assert elapsed < 10
