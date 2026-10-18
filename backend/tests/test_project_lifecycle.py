"""R6 — project lifecycle: archive, restore, duplicate, and the difference.

Two words for two different outcomes, and the audit found only one of them
reachable from the UI:

    archive   reversible. The project leaves the active list and keeps every
              source, version, and learning record.
    delete    the project disappears from everywhere in the app. Nothing is
              erased on disk, but the user cannot get it back.

The dangerous failure is not that Delete exists. It is that the UI offered
Archive under a heading that said "DANGEROUS ACTIONS" and offered no way back,
which taught users that "archive" meant "gone".
"""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import (
    COPVersion,
    LearningProgress,
    Project,
    Source,
    SourceDocument,
)


def make_project(db: Session, title: str = "Lifecycle") -> Project:
    project = Project(title=title, domain="d", scope="s", description="desc")
    db.add(project)
    db.commit()
    return project


def add_source(db: Session, project_id, title: str = "Doc") -> Source:
    source = Source(
        project_id=project_id, type="text", title=title, status="ready", metadata_json={}
    )
    db.add(source)
    db.flush()
    db.add(SourceDocument(source_id=source.id, text="body", content_hash="h", char_count=4))
    db.commit()
    db.refresh(source)
    return source


def add_version(db: Session, project_id, number: int = 1) -> COPVersion:
    version = COPVersion(
        project_id=project_id,
        version_number=number,
        artifact_json={"artifact_id": f"a{number}", "goals": []},
        change_summary="v",
    )
    db.add(version)
    db.commit()
    return version


# --------------------------------------------------------------------------
# Listing
# --------------------------------------------------------------------------


def test_archived_projects_are_hidden_from_the_default_list(client, db) -> None:
    project = make_project(db, "Active")
    other = make_project(db, "Archived")
    client.patch(f"/api/v1/projects/{other.id}", json={"status": "archived"})

    listed = client.get("/api/v1/projects").json()

    ids = {item["id"] for item in listed}
    assert str(project.id) in ids
    assert str(other.id) not in ids


def test_archived_projects_are_listed_on_request(client, db) -> None:
    """Otherwise "where did it go" has no answer."""
    project = make_project(db, "Active")
    archived = make_project(db, "Archived")
    client.patch(f"/api/v1/projects/{archived.id}", json={"status": "archived"})

    listed = client.get("/api/v1/projects", params={"status": "archived"}).json()

    assert [item["id"] for item in listed] == [str(archived.id)]
    assert str(project.id) not in {item["id"] for item in listed}


def test_include_archived_still_returns_both(client, db) -> None:
    """The older flag keeps working; changing its meaning would break callers."""
    project = make_project(db, "Active")
    archived = make_project(db, "Archived")
    client.patch(f"/api/v1/projects/{archived.id}", json={"status": "archived"})

    listed = client.get("/api/v1/projects", params={"include_archived": "true"}).json()

    assert {str(project.id), str(archived.id)} == {item["id"] for item in listed}


# --------------------------------------------------------------------------
# Archive and restore
# --------------------------------------------------------------------------


def test_archiving_keeps_every_source_version_and_progress_record(client, db) -> None:
    """The whole reason Archive exists.

    If archiving dropped a version, "archive, try something else, come back" would
    be a lie.
    """
    project = make_project(db)
    add_source(db, project.id)
    version = add_version(db, project.id)
    db.add(
        LearningProgress(
            project_id=project.id,
            version_id=version.id,
            kind="stage",
            goal_id="goal.a",
            stage_id="stage.a",
            status="completed",
        )
    )
    db.commit()

    client.patch(f"/api/v1/projects/{project.id}", json={"status": "archived"})
    client.post(f"/api/v1/projects/{project.id}/restore")

    assert db.get(COPVersion, version.id) is not None
    assert db.query(Source).filter(Source.project_id == project.id).count() == 1
    progress = list(
        db.scalars(select(LearningProgress).where(LearningProgress.project_id == project.id))
    )
    assert len(progress) == 1
    assert progress[0].status == "completed"


def test_restore_brings_a_project_back_to_the_active_list(client, db) -> None:
    project = make_project(db)
    client.patch(f"/api/v1/projects/{project.id}", json={"status": "archived"})
    assert client.get("/api/v1/projects").json() == []

    restored = client.post(f"/api/v1/projects/{project.id}/restore")

    assert restored.status_code == 200
    assert restored.json()["status"] == "active"
    assert [item["id"] for item in client.get("/api/v1/projects").json()] == [str(project.id)]


def test_restoring_is_idempotent(client, db) -> None:
    """A double-click on Restore must not fail."""
    project = make_project(db)
    client.patch(f"/api/v1/projects/{project.id}", json={"status": "archived"})

    first = client.post(f"/api/v1/projects/{project.id}/restore")
    second = client.post(f"/api/v1/projects/{project.id}/restore")

    assert first.status_code == 200
    assert second.status_code == 200


def test_a_deleted_project_cannot_be_restored(client, db) -> None:
    """Otherwise Delete would be Archive with extra steps."""
    project = make_project(db)
    client.delete(f"/api/v1/projects/{project.id}")

    assert client.post(f"/api/v1/projects/{project.id}/restore").status_code == 404


def test_delete_is_distinguishable_from_archive(client, db) -> None:
    project = make_project(db)
    add_version(db, project.id)

    deleted = client.delete(f"/api/v1/projects/{project.id}")
    archived = make_project(db, "Other")
    client.patch(f"/api/v1/projects/{archived.id}", json={"status": "archived"})

    assert deleted.status_code == 204
    active = {item["id"] for item in client.get("/api/v1/projects").json()}
    archived_ids = {
        item["id"] for item in client.get("/api/v1/projects", params={"status": "archived"}).json()
    }
    assert str(project.id) not in active | archived_ids, "a deleted project must appear nowhere"
    assert str(archived.id) in archived_ids, "an archived project must remain findable"


def test_delete_keeps_the_stored_rows(client, db) -> None:
    """Soft delete, stated as a fact.

    The API reports 204 and the project leaves the UI; the data is still on disk.
    The confirm dialog says so, which is only honest if it is true.
    """
    project = make_project(db)
    version = add_version(db, project.id)

    client.delete(f"/api/v1/projects/{project.id}")

    assert db.get(COPVersion, version.id) is not None
    assert db.get(Project, project.id).status == "deleted"


# --------------------------------------------------------------------------
# Duplicate
# --------------------------------------------------------------------------


def test_duplicate_creates_an_independent_project(client, db) -> None:
    """ "Independent" is the load-bearing word.

    A duplicate sharing rows would be a second name for one project, and
    deleting either would take the other with it.
    """
    project = make_project(db, "Original")
    source = add_source(db, project.id, "Shared-looking title")
    version = add_version(db, project.id)

    copy_summary = client.post(f"/api/v1/projects/{project.id}/duplicate").json()
    copy_id = copy_summary["id"]
    assert copy_id != str(project.id)

    copy_sources = client.get(f"/api/v1/projects/{copy_id}/sources").json()
    assert len(copy_sources) == 1
    assert copy_sources[0]["id"] != str(source.id), "a copied source must be a new row"

    copy_versions = client.get(f"/api/v1/projects/{copy_id}/versions").json()
    assert len(copy_versions) == 1
    assert copy_versions[0]["id"] != str(version.id)
    assert copy_versions[0]["version_number"] == 1, (
        "the copy has no history, so numbering it after the original would imply one"
    )

    # Deleting the original leaves the copy intact.
    client.delete(f"/api/v1/projects/{project.id}")
    assert client.get(f"/api/v1/projects/{copy_id}/versions").json()


def test_duplicate_carries_the_generation_settings(client, db) -> None:
    """Otherwise a copy silently regenerates in a different language or depth."""
    project = make_project(db)
    client.patch(
        f"/api/v1/projects/{project.id}/settings",
        json={"generation": {"language": "zh-CN", "generation_depth": "deep"}},
    )

    copy_id = client.post(f"/api/v1/projects/{project.id}/duplicate").json()["id"]

    effective = client.get(f"/api/v1/projects/{copy_id}/settings").json()["effective"]
    assert effective["generation"]["language"] == "zh-CN"
    assert effective["generation"]["generation_depth"] == "deep"


def test_duplicate_can_skip_the_content(client, db) -> None:
    """A blank project is a legitimate starting point, not a mistake."""
    project = make_project(db)
    add_source(db, project.id)
    add_version(db, project.id)

    copy_id = client.post(
        f"/api/v1/projects/{project.id}/duplicate", params={"with_sources": "false"}
    ).json()["id"]

    assert client.get(f"/api/v1/projects/{copy_id}/versions").json() == []
    assert client.get(f"/api/v1/projects/{copy_id}/sources").json() == []


def test_duplicate_works_before_anything_is_published(client, db) -> None:
    """A user duplicates a project to retry generation, not to copy a version."""
    project = make_project(db)

    response = client.post(f"/api/v1/projects/{project.id}/duplicate")

    assert response.status_code == 200
    assert response.json()["latest_version"] is None


def test_duplicating_an_archived_project_is_allowed(client, db) -> None:
    """Archived does not mean read-only, and refusing would be surprising."""
    project = make_project(db)
    client.patch(f"/api/v1/projects/{project.id}", json={"status": "archived"})

    assert client.post(f"/api/v1/projects/{project.id}/duplicate").status_code == 200


def test_duplicating_a_deleted_project_is_refused(client, db) -> None:
    project = make_project(db)
    client.delete(f"/api/v1/projects/{project.id}")

    assert client.post(f"/api/v1/projects/{project.id}/duplicate").status_code == 404


def test_the_duplicate_title_says_it_is_a_copy(client, db) -> None:
    """Two identically named cards in the library are impossible to tell apart."""
    project = make_project(db, "LangChain agents")

    copy = client.post(f"/api/v1/projects/{project.id}/duplicate").json()

    assert "copy" in copy["title"].lower()
    assert copy["title"] != project.title
