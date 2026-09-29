"""Shared pytest fixtures.

The suite requires a live PostgreSQL, because the behaviour under test
(`FOR UPDATE SKIP LOCKED` claiming, stale-run recovery, the unique
`(run_id, sequence)` constraint) is PostgreSQL-specific, and the V1 spec makes
PostgreSQL the only normative database. The suite fails rather than skipping when
the database is missing, so the persisted Harness is never reported as verified
without actually being executed.

WARNING: the `db` fixture TRUNCATEs every table between cases. Point
TEST_DATABASE_URL at a throwaway database, never at the development database
that Docker Compose uses, or you will delete your own projects and versions.

`make test` and `make test-db` provision the `cop_test` database for you.
"""

import os
import tempfile
from collections.abc import Generator

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session, sessionmaker

TEST_DATABASE_URL = os.environ.get("TEST_DATABASE_URL")

if TEST_DATABASE_URL:
    # The app modules read their configuration at import time, so the test
    # environment has to be established before anything under `app` is imported.
    os.environ["DATABASE_URL"] = TEST_DATABASE_URL
    # A developer may have a live provider in the repository `.env`; tests must
    # stay deterministic and must never spend external API credits.
    os.environ["COP_PROVIDER_MODE"] = "mock"

    # The repository `.env` is written for Docker Compose, where DATA_DIR is the
    # container's /data volume. On a developer machine that path is either absent
    # or read-only, so tests would fail in the app lifespan for a reason that has
    # nothing to do with the code under test.
    os.environ["DATA_DIR"] = os.environ.get(
        "TEST_DATA_DIR",
        os.path.join(tempfile.gettempdir(), "cop-studio-test-data"),
    )

DEVELOPMENT_DATABASE_NAMES = {"cop", "postgres", "template1"}


def _is_development_database() -> bool:
    """True when TEST_DATABASE_URL points at a database that may hold real data.

    Guarding here rather than trusting documentation, because the failure mode is
    silent: a truncated development database looks like a passing test run
    followed by a suddenly empty application.
    """
    name = TEST_DATABASE_URL.rsplit("/", 1)[-1].split("?", 1)[0]
    return name in DEVELOPMENT_DATABASE_NAMES


TRUNCATE_ORDER = (
    "generation_events",
    "generation_runs",
    "source_documents",
    "sources",
    "drafts",
    "learning_progress",
    "cop_versions",
    "project_settings",
    "projects",
    "app_settings",
)


@pytest.fixture(scope="session")
def engine():
    """A migrated PostgreSQL engine for the whole test session.

    Fails rather than skips when `TEST_DATABASE_URL` is missing. These tests
    cover job claiming and crash recovery, the mechanism the whole persisted
    Harness rests on; a silent skip would report a green suite that never
    executed the queue at all.
    """
    if not TEST_DATABASE_URL:
        pytest.fail(
            "TEST_DATABASE_URL must be set to run the backend test suite. Use "
            "'make test-db' to provision the throwaway cop_test database, or set "
            "TEST_DATABASE_URL yourself. Never point it at a database holding "
            "data you want to keep: the db fixture truncates every table."
        )

    if _is_development_database():
        pytest.fail(
            f"Refusing to run tests against {TEST_DATABASE_URL}. The test suite "
            "truncates every table between cases, so it must use a throwaway "
            "database. Run 'make test' or set TEST_DATABASE_NAME to a database "
            "other than the one Docker Compose uses."
        )

    from app.db.models import Base

    test_engine = create_engine(TEST_DATABASE_URL, pool_pre_ping=True)
    Base.metadata.create_all(test_engine)
    yield test_engine
    test_engine.dispose()


@pytest.fixture
def db(engine) -> Generator[Session, None, None]:
    """A clean database for each test."""
    with engine.begin() as connection:
        connection.execute(text(f"TRUNCATE {', '.join(TRUNCATE_ORDER)} RESTART IDENTITY CASCADE"))
    factory = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
    with factory() as session:
        yield session


@pytest.fixture
def client(db) -> Generator:
    from fastapi.testclient import TestClient

    from app.db.session import get_db
    from app.main import app

    def override_get_db() -> Generator[Session, None, None]:
        yield db

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
