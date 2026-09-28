from pathlib import Path

from sqlalchemy import select

from app.db.models import COPVersion, Project
from app.db.session import SessionLocal
from app.domain.validation import load_json, validate_artifact


def find_asset(relative_path: str) -> Path:
    candidates = [
        Path.cwd() / relative_path,
        Path.cwd().parent / relative_path,
        Path("/app") / relative_path,
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    raise FileNotFoundError(relative_path)


def main() -> None:
    fixture_path = find_asset("fixtures/reference-langchain-cop.json")
    schema_path = find_asset("schemas/cop-artifact.schema.json")
    artifact = validate_artifact(load_json(fixture_path), schema_path)

    with SessionLocal() as session:
        existing = session.scalar(select(Project).where(Project.domain == artifact.domain.name))
        if existing is not None:
            print(f"Reference project already exists: {existing.id}")
            return
        project = Project(
            title=artifact.domain.name,
            description=artifact.mental_model.summary,
            domain=artifact.domain.name,
            scope=artifact.domain.scope,
            preferred_language=artifact.metadata.language,
        )
        session.add(project)
        session.flush()
        version = COPVersion(
            project_id=project.id,
            version_number=1,
            artifact_json=artifact.model_dump(mode="json"),
            change_summary="Imported validated LangChain reference COP",
            created_by="harness",
        )
        session.add(version)
        session.commit()
        print(f"Seeded project {project.id} with version {version.id}")


if __name__ == "__main__":
    main()
