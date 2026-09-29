"""M8 export acceptance: JSON, one Markdown file, and a readable bundle."""

import io
import json
import zipfile
from pathlib import Path

from app.db.models import COPVersion, Project

FIXTURE = Path(__file__).resolve().parents[2] / "fixtures" / "reference-langchain-cop.json"


def publish(db) -> tuple[str, str, dict]:
    artifact = json.loads(FIXTURE.read_text(encoding="utf-8"))
    project = Project(title="Export", domain="Export", scope="s")
    db.add(project)
    db.flush()
    version = COPVersion(
        project_id=project.id,
        version_number=1,
        artifact_json=artifact,
        change_summary="v1",
        created_by="harness",
    )
    db.add(version)
    db.commit()
    return str(project.id), str(version.id), artifact


def export(client, version_id: str, format_name: str):
    return client.post(f"/api/v1/versions/{version_id}/exports", json={"format": format_name})


def test_json_export_is_the_exact_published_artifact(client, db):
    _project_id, version_id, artifact = publish(db)
    response = export(client, version_id, "json")

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("application/json")
    assert response.json() == artifact
    assert ".json" in response.headers["content-disposition"]


def test_single_markdown_is_human_readable_without_the_app(client, db):
    _project_id, version_id, artifact = publish(db)
    response = export(client, version_id, "markdown")
    text = response.content.decode()

    assert response.status_code == 200
    assert "-v1.md" in response.headers["content-disposition"]
    assert text.startswith(f"# {artifact['domain']['name']}")
    assert "## Mental model" in text
    assert "## Goals and main processes" in text
    assert artifact["stages"][0]["title"] in text
    assert artifact["concepts"][0]["name"] in text
    assert artifact["operations"][0]["name"] in text


def test_browser_can_read_the_export_filename_header(client, db):
    _project_id, version_id, _artifact = publish(db)
    response = client.post(
        f"/api/v1/versions/{version_id}/exports",
        json={"format": "markdown"},
        headers={"Origin": "http://localhost:3000"},
    )

    assert response.status_code == 200
    exposed = response.headers["access-control-expose-headers"].lower()
    assert "content-disposition" in exposed


def test_markdown_bundle_contains_standalone_readable_files(client, db):
    _project_id, version_id, artifact = publish(db)
    response = export(client, version_id, "markdown_bundle")

    assert response.status_code == 200
    with zipfile.ZipFile(io.BytesIO(response.content)) as archive:
        names = archive.namelist()
        assert "README.md" in names
        assert "artifact.json" in names
        assert len([name for name in names if name.startswith("stages/")]) == len(
            artifact["stages"]
        )
        assert any(name.startswith("concepts/") for name in names)
        assert any(name.startswith("operations/") for name in names)
        for name in names:
            if name.endswith(".md"):
                assert archive.read(name).decode().strip(), f"{name} must be readable text"


def test_export_does_not_modify_the_version(client, db):
    _project_id, version_id, artifact = publish(db)
    export(client, version_id, "markdown")
    stored = client.get(f"/api/v1/versions/{version_id}").json()["artifact"]
    assert stored == artifact


def test_unknown_version_cannot_be_exported(client, db):
    import uuid

    response = export(client, str(uuid.uuid4()), "json")
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "VERSION_NOT_FOUND"
