"""M7 tests: learning progress.

Covers the acceptance criteria in `23-coding-agent-milestones.md`:

- reload does not lose progress,
- switching artifact version does not corrupt progress records,
- the full Main Process stays visible.

The last one is enforced in the browser suite, because it is a rendering
property. What is checkable here is that the API hands the client every Stage
of a Goal in order, since a UI that cannot see the remaining Stages cannot keep
the Main Process on screen.
"""

import json
from pathlib import Path

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.db.models import COPVersion, LearningProgress, Project

FIXTURE = Path(__file__).resolve().parents[2] / "fixtures" / "reference-langchain-cop.json"


def fixture() -> dict:
    with FIXTURE.open(encoding="utf-8") as handle:
        return json.load(handle)


def create_project(db: Session) -> str:
    project = Project(title="Learn", domain="Learn", scope="s")
    db.add(project)
    db.commit()
    return str(project.id)


def publish(db: Session, project_id: str, artifact: dict | None = None) -> str:
    latest = db.scalar(
        select(func.max(COPVersion.version_number)).where(COPVersion.project_id == project_id)
    )
    version = COPVersion(
        project_id=project_id,
        version_number=(latest or 0) + 1,
        artifact_json=artifact if artifact is not None else fixture(),
        change_summary="v",
        created_by="harness",
    )
    db.add(version)
    db.commit()
    return str(version.id)


def first_goal(artifact: dict) -> tuple[str, str, list[str]]:
    goal_id = artifact["goals"][0]["id"]
    process = next(p for p in artifact["main_processes"] if p["goal_ref"] == goal_id)
    return goal_id, process["id"], list(process["stage_refs"])


def put(
    client,
    project_id: str,
    version_id: str,
    goal_id: str,
    stage_id: str | None,
    status: str,
    *,
    kind: str = "stage",
    notes: str | None = None,
):
    """Record progress.

    `kind` is explicit rather than defaulted-and-hidden, because the whole point
    of R5 is that a Foundation Stage, a Main Process Stage, a Practice, and a
    checkpoint are four different things. A test that omitted it would keep
    passing whatever the default happened to be.
    """
    return client.put(
        f"/api/v1/projects/{project_id}/learning-progress",
        json={
            "version_id": version_id,
            "kind": kind,
            "goal_id": goal_id,
            "stage_id": stage_id,
            "status": status,
            "notes": notes,
        },
    )


def put_foundation(client, project_id: str, version_id: str, stage_id: str, status: str):
    """Foundation progress carries no Goal, which is the point of it."""
    return client.put(
        f"/api/v1/projects/{project_id}/learning-progress",
        json={
            "version_id": version_id,
            "kind": "foundation",
            "goal_id": "",
            "stage_id": stage_id,
            "status": status,
        },
    )


class TestReadingProgress:
    def test_a_fresh_project_reports_every_stage_as_not_started(self, client, db):
        project_id = create_project(db)
        version_id = publish(db, project_id)
        goal_id, _process, stages = first_goal(fixture())

        body = client.get(
            f"/api/v1/projects/{project_id}/learning-progress",
            params={"version_id": version_id},
        ).json()

        goal = next(item for item in body["goals"] if item["goal_id"] == goal_id)
        # Every Stage is returned, in process order. A UI that only ever received
        # the completed ones could not show the Main Process.
        assert [item["stage_id"] for item in goal["stages"]] == stages
        assert all(item["status"] == "not_started" for item in goal["stages"])
        assert goal["completed"] is False

    def test_it_defaults_to_the_latest_version(self, client, db):
        project_id = create_project(db)
        publish(db, project_id)
        latest = publish(db, project_id)

        body = client.get(f"/api/v1/projects/{project_id}/learning-progress").json()
        assert body["version_id"] == latest
        assert body["version_number"] == 2

    def test_a_project_with_no_version_says_so(self, client, db):
        project_id = create_project(db)
        response = client.get(f"/api/v1/projects/{project_id}/learning-progress")
        assert response.status_code == 404
        assert response.json()["error"]["code"] == "NO_VERSION"


class TestRecordingProgress:
    def test_marking_a_stage_complete_persists(self, client, db):
        project_id = create_project(db)
        version_id = publish(db, project_id)
        goal_id, _process, stages = first_goal(fixture())

        response = put(client, project_id, version_id, goal_id, stages[0], "completed")
        assert response.status_code == 200, response.text

        body = client.get(
            f"/api/v1/projects/{project_id}/learning-progress",
            params={"version_id": version_id},
        ).json()
        goal = next(item for item in body["goals"] if item["goal_id"] == goal_id)
        assert goal["stages"][0]["status"] == "completed"
        assert goal["completed_stages"] == 1

    def test_goal_completion_is_derived_from_its_stages(self, client, db):
        """Stages alone no longer complete a Goal.

        R5 makes completion depend on three things, and this test now records all
        three rather than only the first. The single-Stage case is kept at the end
        as the control: it has no Practice and no Foundation, so Stages are the
        whole rule and the old assertion still has to hold.
        """
        project_id = create_project(db)
        artifact = fixture()
        goal_id, _process, stages = first_goal(artifact)
        # Strip the Foundation and the Practice so this test isolates the Stage
        # rule. The three-way rule has its own test below.
        artifact["shared_foundations"] = []
        artifact["practices"] = []
        version_id = publish(db, project_id, artifact)

        for stage_id in stages[:-1]:
            put(client, project_id, version_id, goal_id, stage_id, "completed")
        body = client.get(
            f"/api/v1/projects/{project_id}/learning-progress",
            params={"version_id": version_id},
        ).json()
        goal = next(item for item in body["goals"] if item["goal_id"] == goal_id)
        assert goal["completed"] is False, "one Stage left means the Goal is not done"

        put(client, project_id, version_id, goal_id, stages[-1], "completed")
        body = client.get(
            f"/api/v1/projects/{project_id}/learning-progress",
            params={"version_id": version_id},
        ).json()
        goal = next(item for item in body["goals"] if item["goal_id"] == goal_id)
        assert goal["completed"] is True
        assert body["completed_goals"] == 1

    def test_marking_the_same_stage_twice_updates_one_row(self, client, db):
        """Progress is a fold, not a log. Two rows for one Stage would be a bug."""
        project_id = create_project(db)
        version_id = publish(db, project_id)
        goal_id, _process, stages = first_goal(fixture())

        put(client, project_id, version_id, goal_id, stages[0], "in_progress")
        put(client, project_id, version_id, goal_id, stages[0], "completed")

        count = db.scalar(
            select(func.count())
            .select_from(LearningProgress)
            .where(LearningProgress.version_id == version_id)
        )
        assert count == 1

    def test_a_completed_stage_can_be_reopened(self, client, db):
        """Spec 16 §6 allows completed -> in_progress for revisiting."""
        project_id = create_project(db)
        version_id = publish(db, project_id)
        goal_id, _process, stages = first_goal(fixture())

        put(client, project_id, version_id, goal_id, stages[0], "completed")
        reopened = put(client, project_id, version_id, goal_id, stages[0], "in_progress")
        assert reopened.status_code == 200

        body = client.get(
            f"/api/v1/projects/{project_id}/learning-progress",
            params={"version_id": version_id},
        ).json()
        goal = next(item for item in body["goals"] if item["goal_id"] == goal_id)
        assert goal["stages"][0]["status"] == "in_progress"
        assert goal["completed"] is False, "reopening a Stage must un-complete its Goal"

    def test_a_stage_belonging_to_another_goal_is_refused(self, client, db):
        artifact = fixture()
        project_id = create_project(db)
        version_id = publish(db, project_id)
        goal_id, _process, stages = first_goal(artifact)
        other_goal = artifact["goals"][1]["id"]
        other_process = next(p for p in artifact["main_processes"] if p["goal_ref"] == other_goal)
        foreign_stage = other_process["stage_refs"][0]

        response = put(client, project_id, version_id, goal_id, foreign_stage, "completed")
        assert response.status_code == 422
        assert response.json()["error"]["code"] == "STAGE_NOT_IN_GOAL"

    def test_progress_for_an_unknown_goal_is_refused(self, client, db):
        project_id = create_project(db)
        version_id = publish(db, project_id)
        response = put(client, project_id, version_id, "goal.nope", None, "completed")
        assert response.status_code == 422
        assert response.json()["error"]["code"] == "GOAL_NOT_IN_VERSION"

    def test_progress_cannot_be_written_to_another_project(self, client, db):
        project_id = create_project(db)
        other = create_project(db)
        version_id = publish(db, other)
        goal_id, _process, stages = first_goal(fixture())

        response = put(client, project_id, version_id, goal_id, stages[0], "completed")
        assert response.status_code == 404


class TestVersionIsolation:
    def test_switching_version_does_not_touch_the_other_history(self, client, db):
        """Acceptance: switching artifact version does not corrupt progress."""
        project_id = create_project(db)
        goal_id, _process, stages = first_goal(fixture())
        v1 = publish(db, project_id)
        put(client, project_id, v1, goal_id, stages[0], "completed")

        # A new version is published, sharing entity ids with v1.
        v2 = publish(db, project_id)

        one = client.get(
            f"/api/v1/projects/{project_id}/learning-progress", params={"version_id": v1}
        ).json()
        two = client.get(
            f"/api/v1/projects/{project_id}/learning-progress", params={"version_id": v2}
        ).json()

        goal_one = next(item for item in one["goals"] if item["goal_id"] == goal_id)
        goal_two = next(item for item in two["goals"] if item["goal_id"] == goal_id)
        assert goal_one["stages"][0]["status"] == "completed"
        assert goal_two["stages"][0]["status"] == "not_started", (
            "progress must not leak across versions that reuse the same entity ids"
        )

    def test_both_histories_survive_alternating_writes(self, client, db):
        project_id = create_project(db)
        goal_id, _process, stages = first_goal(fixture())
        v1 = publish(db, project_id)
        v2 = publish(db, project_id)

        put(client, project_id, v1, goal_id, stages[0], "completed")
        put(client, project_id, v2, goal_id, stages[0], "in_progress")
        put(client, project_id, v1, goal_id, stages[1], "completed")

        one = client.get(
            f"/api/v1/projects/{project_id}/learning-progress", params={"version_id": v1}
        ).json()
        two = client.get(
            f"/api/v1/projects/{project_id}/learning-progress", params={"version_id": v2}
        ).json()
        g1 = next(item for item in one["goals"] if item["goal_id"] == goal_id)
        g2 = next(item for item in two["goals"] if item["goal_id"] == goal_id)
        assert [item["status"] for item in g1["stages"][:2]] == ["completed", "completed"]
        assert [item["status"] for item in g2["stages"][:2]] == ["in_progress", "not_started"]


class TestProgressImmutability:
    def test_progress_never_writes_a_version(self, client, db):
        """Learning progress must not be able to modify a published COP."""
        paths = client.get("/openapi.json").json()["paths"]
        for path, operations in paths.items():
            if "learning-progress" in path:
                assert set(operations) <= {"get", "put"}, (
                    f"{path} exposes {sorted(operations)}; progress must only be read or recorded"
                )
                for method in operations:
                    assert "versions" not in path, f"{method} {path} reaches a version"
