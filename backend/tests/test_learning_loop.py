"""R5 — the learning loop closes.

A Stage checkbox was the whole of M7. A learner could read a Practice and tick
every Stage, and the app reported the Goal complete while the Practice was never
attempted and the Foundation they build on was never opened.

Completion is now derived from three inputs, and each is tested on its own
because each fails on its own:

    Foundation   the shared setup every process starts from
    Stages       the main line, as before
    Practice     the exercise, and its checkpoint answers

`blocked_by` is part of the contract, not a convenience: a Goal that shows an
empty progress bar and no reason is indistinguishable from a broken bar.
"""

import json
from pathlib import Path

import pytest
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


def publish(db: Session, project_id: str, artifact: dict) -> str:
    """Publish the next version, reading the number inside the session.

    The number comes from the table rather than from a parameter, so calling this
    twice produces v1 and v2 without the caller having to know the current
    count -- and a hand-numbered insert can collide with the
    `(project_id, version_number)` unique constraint in a way that looks like a
    missing version.
    """
    latest = db.scalar(
        select(func.max(COPVersion.version_number)).where(COPVersion.project_id == project_id)
    )
    version = COPVersion(
        project_id=project_id,
        version_number=(latest or 0) + 1,
        artifact_json=artifact,
        change_summary="v",
    )
    db.add(version)
    db.commit()
    return str(version.id)


def goal_fixture(goal_index: int = 0) -> tuple[dict, str, list[str], str | None, list[str]]:
    """A Goal plus its Stages, its Foundation Stages, and its Practice.

    The Foundation is read from the API rather than from the fixture in each
    test, because the API is what decides which Stages are Foundation Stages and
    duplicating that rule here would let the two disagree unnoticed.
    """
    artifact = fixture()
    goal = artifact["goals"][goal_index]
    goal_id = str(goal["id"])
    process = next(p for p in artifact["main_processes"] if p["goal_ref"] == goal_id)
    stages = list(process["stage_refs"])
    practice = next((p for p in artifact["practices"] if p["goal_ref"] == goal_id), None)
    return (
        artifact,
        goal_id,
        stages,
        practice["id"] if practice else None,
        [str(q) for q in (practice or {}).get("checkpoint_questions") or []],
    )


def read(client, project_id: str, version_id: str) -> dict:
    return client.get(
        f"/api/v1/projects/{project_id}/learning-progress",
        params={"version_id": version_id},
    ).json()


def put(client, project_id, version_id, **body):
    return client.put(
        f"/api/v1/projects/{project_id}/learning-progress",
        json={"version_id": version_id, **body},
    )


def goal_of(body: dict, goal_id: str) -> dict:
    return next(item for item in body["goals"] if item["goal_id"] == goal_id)


def foundation_stages(client, project_id, version_id) -> list[str]:
    return [item["stage_id"] for item in read(client, project_id, version_id)["foundations"]]


def complete_except_practice(client, project_id, version_id, goal_id, stages) -> None:
    """Everything a Goal needs except its Practice.

    Named for what it deliberately leaves undone, because that is the whole point:
    the Practice is the one blocker these tests isolate.
    """
    for stage_id in foundation_stages(client, project_id, version_id):
        response = put(
            client,
            project_id,
            version_id,
            kind="foundation",
            goal_id="",
            stage_id=stage_id,
            status="completed",
        )
        assert response.status_code == 200, response.text
    for stage_id in stages:
        response = put(
            client,
            project_id,
            version_id,
            kind="stage",
            goal_id=goal_id,
            stage_id=stage_id,
            status="completed",
        )
        assert response.status_code == 200, response.text


# --------------------------------------------------------------------------
# Foundation
# --------------------------------------------------------------------------


def test_foundation_progress_is_listed_and_starts_empty(client, db):
    artifact, goal_id, _stages, _practice, _questions = goal_fixture()
    project_id = create_project(db)
    version_id = publish(db, project_id, artifact)

    body = read(client, project_id, version_id)

    assert body["foundations"], "the shared Foundation must be visible, not implicit"
    assert all(item["status"] == "not_started" for item in body["foundations"])


def test_a_stage_is_not_complete_while_its_foundation_is_open(client, db):
    """The gap R5 exists to close.

    Every Main Process starts at the same Foundation Stages, so a Goal could show
    complete while the shared setup was never opened.
    """
    artifact, goal_id, stages, _practice, _questions = goal_fixture()
    project_id = create_project(db)
    version_id = publish(db, project_id, artifact)

    for stage_id in stages:
        put(
            client,
            project_id,
            version_id,
            kind="stage",
            goal_id=goal_id,
            stage_id=stage_id,
            status="completed",
        )

    goal = goal_of(read(client, project_id, version_id), goal_id)

    assert goal["completed"] is False
    assert any("Foundation" in reason for reason in goal["blocked_by"]), goal["blocked_by"]


def test_completing_the_foundation_unblocks_the_goal(client, db):
    artifact, goal_id, stages, _practice, _questions = goal_fixture()
    project_id = create_project(db)
    version_id = publish(db, project_id, artifact)
    foundation = foundation_stages(client, project_id, version_id)
    for stage_id in stages:
        put(
            client,
            project_id,
            version_id,
            kind="stage",
            goal_id=goal_id,
            stage_id=stage_id,
            status="completed",
        )

    for stage_id in foundation:
        put(
            client,
            project_id,
            version_id,
            kind="foundation",
            goal_id="",
            stage_id=stage_id,
            status="completed",
        )

    goal = goal_of(read(client, project_id, version_id), goal_id)
    # Foundation and Stages are done, so the only thing left can be the Practice.
    assert not any("Foundation" in reason for reason in goal["blocked_by"])
    assert any("Practice" in reason for reason in goal["blocked_by"]), goal["blocked_by"]


def test_foundation_progress_is_shared_across_goals(client, db):
    """One Foundation, recorded once.

    Storing it per Goal would make "have I done the setup" depend on which Goal
    the user happened to be looking at.
    """
    artifact, goal_id, _stages, _practice, _questions = goal_fixture(0)
    other = artifact["goals"][1]
    project_id = create_project(db)
    version_id = publish(db, project_id, artifact)
    foundation = foundation_stages(client, project_id, version_id)

    for stage_id in foundation:
        put(
            client,
            project_id,
            version_id,
            kind="foundation",
            goal_id="",
            stage_id=stage_id,
            status="completed",
        )

    body = read(client, project_id, version_id)

    assert all(item["status"] == "completed" for item in body["foundations"])
    rows = list(
        db.scalars(
            select(LearningProgress).where(
                LearningProgress.project_id == project_id, LearningProgress.kind == "foundation"
            )
        )
    )
    assert len(rows) == len(foundation), (
        "the shared Foundation must be stored once, not once per Goal"
    )
    assert {str(other["id"])} != {goal_id}


def test_a_foundation_stage_cannot_be_recorded_under_a_goal(client, db):
    """Sending a goal_id would re-create the per-Goal duplication."""
    artifact, _goal_id, _stages, _practice, _questions = goal_fixture()
    project_id = create_project(db)
    version_id = publish(db, project_id, artifact)
    foundation = foundation_stages(client, project_id, version_id)

    response = put(
        client,
        project_id,
        version_id,
        kind="foundation",
        goal_id=artifact["goals"][0]["id"],
        stage_id=foundation[0],
        status="completed",
    )

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "FOUNDATION_NEEDS_NO_GOAL"


def test_a_main_process_stage_cannot_be_recorded_as_foundation(client, db):
    artifact, goal_id, stages, _practice, _questions = goal_fixture()
    project_id = create_project(db)
    version_id = publish(db, project_id, artifact)

    response = put(
        client,
        project_id,
        version_id,
        kind="foundation",
        goal_id="",
        stage_id=stages[0],
        status="completed",
    )

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "STAGE_NOT_FOUNDATION"


# --------------------------------------------------------------------------
# Practice and checkpoints
# --------------------------------------------------------------------------


def test_practice_progress_is_reported_with_its_questions(client, db):
    artifact, goal_id, _stages, _practice, questions = goal_fixture()
    project_id = create_project(db)
    version_id = publish(db, project_id, artifact)

    goal = goal_of(read(client, project_id, version_id), goal_id)

    assert goal["practice"] is not None
    assert goal["practice"]["status"] == "not_started"
    assert [item["question"] for item in goal["practice"]["checkpoints"]] == questions
    assert all(item["answer"] is None for item in goal["practice"]["checkpoints"])


def test_a_goal_is_not_complete_while_its_practice_is_untouched(client, db):
    artifact, goal_id, stages, _practice, _questions = goal_fixture()
    project_id = create_project(db)
    version_id = publish(db, project_id, artifact)
    complete_except_practice(client, project_id, version_id, goal_id, stages)

    goal = goal_of(read(client, project_id, version_id), goal_id)

    assert goal["completed"] is False
    assert any("not started" in reason for reason in goal["blocked_by"]), goal["blocked_by"]


def test_answering_a_checkpoint_alone_does_not_complete_the_practice(client, db):
    """Answers are necessary, not sufficient.

    Otherwise a learner could satisfy the requirement by typing one character
    into each box without attempting the exercise.
    """
    artifact, goal_id, stages, _practice, questions = goal_fixture()
    project_id = create_project(db)
    version_id = publish(db, project_id, artifact)
    complete_except_practice(client, project_id, version_id, goal_id, stages)

    for index, question in enumerate(questions):
        put(
            client,
            project_id,
            version_id,
            kind="checkpoint",
            goal_id=goal_id,
            stage_id=question,
            status="completed",
            notes=f"answer {index}",
        )

    goal = goal_of(read(client, project_id, version_id), goal_id)

    assert goal["practice"]["status"] == "in_progress"
    assert goal["completed"] is False
    assert any("not marked complete" in reason for reason in goal["blocked_by"]), goal["blocked_by"]


def test_answered_questions_survive_a_reload(client, db):
    artifact, goal_id, _stages, _practice, questions = goal_fixture()
    project_id = create_project(db)
    version_id = publish(db, project_id, artifact)
    put(
        client,
        project_id,
        version_id,
        kind="checkpoint",
        goal_id=goal_id,
        stage_id=questions[0],
        status="completed",
        notes="The agent harness wraps the model.",
    )

    goal = goal_of(read(client, project_id, version_id), goal_id)
    first = goal["practice"]["checkpoints"][0]

    assert first["answer"] == "The agent harness wraps the model."
    assert first["updated_at"] is not None, "an answer with no timestamp cannot be audited"


def test_completing_the_practice_closes_the_goal(client, db):
    artifact, goal_id, stages, _practice, questions = goal_fixture()
    project_id = create_project(db)
    version_id = publish(db, project_id, artifact)
    complete_except_practice(client, project_id, version_id, goal_id, stages)
    for index, question in enumerate(questions):
        put(
            client,
            project_id,
            version_id,
            kind="checkpoint",
            goal_id=goal_id,
            stage_id=question,
            status="completed",
            notes=f"answer {index}",
        )
    put(
        client,
        project_id,
        version_id,
        kind="practice",
        goal_id=goal_id,
        status="completed",
    )

    body = read(client, project_id, version_id)
    goal = goal_of(body, goal_id)

    assert goal["completed"] is True, goal["blocked_by"]
    assert body["completed_goals"] == 1


def test_an_answer_to_a_question_nobody_asked_is_rejected(client, db):
    artifact, goal_id, _stages, _practice, _questions = goal_fixture()
    project_id = create_project(db)
    version_id = publish(db, project_id, artifact)

    response = put(
        client,
        project_id,
        version_id,
        kind="checkpoint",
        goal_id=goal_id,
        stage_id="A question this Practice does not ask",
        status="completed",
        notes="answer",
    )

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "CHECKPOINT_NOT_IN_PRACTICE"


def test_an_empty_answer_is_rejected(client, db):
    """Clearing a question is a delete, not an empty write.

    Accepting an empty answer would let the "all questions answered" rule be
    satisfied by whitespace.
    """
    artifact, goal_id, _stages, _practice, questions = goal_fixture()
    project_id = create_project(db)
    version_id = publish(db, project_id, artifact)

    response = put(
        client,
        project_id,
        version_id,
        kind="checkpoint",
        goal_id=goal_id,
        stage_id=questions[0],
        status="completed",
        notes="   ",
    )

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "CHECKPOINT_ANSWER_REQUIRED"


def test_re_answering_a_question_replaces_the_answer(client, db):
    artifact, goal_id, _stages, _practice, questions = goal_fixture()
    project_id = create_project(db)
    version_id = publish(db, project_id, artifact)
    for answer in ("first attempt", "corrected after re-reading"):
        put(
            client,
            project_id,
            version_id,
            kind="checkpoint",
            goal_id=goal_id,
            stage_id=questions[0],
            status="completed",
            notes=answer,
        )

    checkpoints = goal_of(read(client, project_id, version_id), goal_id)["practice"]["checkpoints"]
    answers = [item["answer"] for item in checkpoints if item["question"] == questions[0]]

    assert answers == ["corrected after re-reading"], (
        "a second answer must update the row, not add a second one"
    )


def test_progress_for_a_goal_with_no_practice_ignores_the_practice_rule(client, db):
    """A COP without Practices must still be completable.

    Otherwise R5 would make a valid artifact permanently uncompletable.
    """
    artifact, goal_id, stages, _practice, _questions = goal_fixture()
    artifact["practices"] = []
    artifact["shared_foundations"] = []
    project_id = create_project(db)
    version_id = publish(db, project_id, artifact)
    for stage_id in stages:
        put(
            client,
            project_id,
            version_id,
            kind="stage",
            goal_id=goal_id,
            stage_id=stage_id,
            status="completed",
        )

    goal = goal_of(read(client, project_id, version_id), goal_id)

    assert goal["practice"] is None
    assert goal["completed"] is True


# --------------------------------------------------------------------------
# Isolation and persistence
# --------------------------------------------------------------------------


def test_v1_and_v2_learning_records_do_not_mix(client, db):
    """A Foundation completed in v1 must not make v2 look done.

    v2 reuses entity ids on purpose in the real product, so a shared key here
    would silently carry progress across histories.
    """
    artifact, goal_id, stages, _practice, _questions = goal_fixture()
    project_id = create_project(db)
    v1 = publish(db, project_id, artifact)
    # Same ids, different content, exactly as a revised publish produces.
    revised = json.loads(json.dumps(artifact))
    revised["artifact_id"] = "artifact.v2"
    # Same entity ids, different content: a v1 row must not satisfy a v2 read.
    revised["goals"][0]["title"] = f"{artifact['goals'][0]['title']} (v2)"
    v2_id = publish(db, project_id, revised)

    foundation = foundation_stages(client, project_id, v1)
    for stage_id in foundation:
        put(
            client,
            project_id,
            v1,
            kind="foundation",
            goal_id="",
            stage_id=stage_id,
            status="completed",
        )
    for stage_id in stages:
        put(
            client,
            project_id,
            v1,
            kind="stage",
            goal_id=goal_id,
            stage_id=stage_id,
            status="completed",
        )

    fresh = goal_of(read(client, project_id, v2_id), goal_id)

    assert fresh["completed_stages"] == 0
    assert all(
        item["status"] == "not_started" for item in read(client, project_id, v2_id)["foundations"]
    )
    # And v1 is untouched by looking at v2.
    assert goal_of(read(client, project_id, v1), goal_id)["completed_stages"] == len(stages)


def test_a_second_device_writing_the_same_activity_updates_one_row(client, db):
    """The unique index, exercised.

    Two concurrent writes without it would leave two rows and every read would
    have to guess which wins.
    """
    artifact, goal_id, stages, _practice, _questions = goal_fixture()
    project_id = create_project(db)
    version_id = publish(db, project_id, artifact)
    stage_id = stages[0]

    for status in ("in_progress", "completed", "in_progress"):
        put(
            client,
            project_id,
            version_id,
            kind="stage",
            goal_id=goal_id,
            stage_id=stage_id,
            status=status,
        )

    rows = list(
        db.scalars(
            select(LearningProgress).where(
                LearningProgress.project_id == project_id,
                LearningProgress.version_id == version_id,
                LearningProgress.stage_id == stage_id,
            )
        )
    )

    assert len(rows) == 1
    assert rows[0].status == "in_progress"


def test_a_foundation_row_and_a_stage_row_for_the_same_stage_coexist(client, db):
    """Two activities, two rows.

    A Stage that is part of the Foundation is a Stage the user can meet in two
    places. The old index could not tell those rows apart because both have a
    NULL goal_id.
    """
    artifact, _goal_id, _stages, _practice, _questions = goal_fixture()
    project_id = create_project(db)
    version_id = publish(db, project_id, artifact)
    foundation = foundation_stages(client, project_id, version_id)

    put(
        client,
        project_id,
        version_id,
        kind="foundation",
        goal_id="",
        stage_id=foundation[0],
        status="completed",
    )

    rows = list(
        db.scalars(
            select(LearningProgress).where(
                LearningProgress.project_id == project_id,
                LearningProgress.stage_id == foundation[0],
            )
        )
    )
    assert len(rows) == 1
    assert rows[0].kind == "foundation"


def test_a_completed_activity_can_still_be_reopened(client, db):
    """Revisiting is legitimate; that is why `completed -> in_progress` is legal."""
    artifact, goal_id, stages, _practice, _questions = goal_fixture()
    project_id = create_project(db)
    version_id = publish(db, project_id, artifact)
    stage_id = stages[0]

    put(
        client,
        project_id,
        version_id,
        kind="stage",
        goal_id=goal_id,
        stage_id=stage_id,
        status="completed",
    )
    response = put(
        client,
        project_id,
        version_id,
        kind="stage",
        goal_id=goal_id,
        stage_id=stage_id,
        status="in_progress",
    )

    assert response.status_code == 200
    goal = goal_of(read(client, project_id, version_id), goal_id)
    assert goal["completed_stages"] == 0


def test_progress_survives_a_service_restart(client, db):
    """The stored rows are the record; nothing lives in the client.

    Re-reading through the API in a fresh request is as close to a restart as a
    test can get without tearing the container down, and it is the property that
    matters: no in-process state.
    """
    artifact, goal_id, stages, _practice, questions = goal_fixture()
    project_id = create_project(db)
    version_id = publish(db, project_id, artifact)
    put(
        client,
        project_id,
        version_id,
        kind="stage",
        goal_id=goal_id,
        stage_id=stages[0],
        status="completed",
    )
    put(
        client,
        project_id,
        version_id,
        kind="checkpoint",
        goal_id=goal_id,
        stage_id=questions[0],
        status="completed",
        notes="remembered",
    )

    # A brand-new session, as a restarted API would have.
    with db.get_bind().connect() as connection:
        connection.exec_driver_sql("SELECT 1")

    goal = goal_of(read(client, project_id, version_id), goal_id)

    assert goal["stages"][0]["status"] == "completed"
    assert goal["practice"]["checkpoints"][0]["answer"] == "remembered"


@pytest.mark.parametrize("kind", ["foundation", "stage", "practice", "checkpoint"])
def test_every_kind_rejects_a_stage_that_does_not_exist(client, db, kind):
    artifact, goal_id, _stages, _practice, _questions = goal_fixture()
    project_id = create_project(db)
    version_id = publish(db, project_id, artifact)

    if kind in {"practice", "checkpoint"}:
        body = {
            "kind": kind,
            "goal_id": goal_id,
            "stage_id": "no-such-thing",
            "status": "completed",
            "notes": "x",
        }
    else:
        body = {
            "kind": kind,
            "goal_id": "" if kind == "foundation" else goal_id,
            "stage_id": "no-such-stage",
            "status": "completed",
        }

    assert put(client, project_id, version_id, **body).status_code == 422
