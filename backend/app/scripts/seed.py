from pathlib import Path

from sqlalchemy import select

from app.db.models import COPVersion, Project, ProjectSettings, Source, SourceDocument
from app.db.session import SessionLocal
from app.domain.validation import load_json, validate_artifact
from app.research.snapshots import content_hash


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


def _seed_sources(session, project_id) -> list[Source]:
    """Create the Sources the fixture's evidence refs point at.

    Without this the seeded artifact cites six source ids that resolve to nothing,
    which is the R3 orphan-reference failure: the user sees a claim marked as
    sourced and has nothing to open. Each `Source.metadata_json.research_source_id`
    holds the id the artifact uses, so resolution matches the citation rather than
    the row's primary key.
    """
    sources_path = find_asset("fixtures/reference-langchain-sources.json")
    declared = load_json(sources_path)
    created: list[Source] = []
    for entry in declared:
        source_id = str(entry["id"])
        source = Source(
            project_id=project_id,
            type="url",
            title=str(entry["title"])[:300],
            original_uri=str(entry.get("original_uri") or "") or None,
            status="ready",
            metadata_json={"provider": "reference", "research_source_id": source_id},
        )
        session.add(source)
        session.flush()
        text = str(entry.get("text") or "")
        session.add(
            SourceDocument(
                source_id=source.id,
                text=text,
                content_hash=content_hash(text),
                char_count=len(text),
            )
        )
        created.append(source)
    return created


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
        _seed_sources(session, project.id)
        # The reference is a `deep` artifact; seeding it with the app default would
        # mean regenerating this project produces something visibly smaller.
        session.add(
            ProjectSettings(
                project_id=project.id,
                settings_json={
                    "generation": {
                        "generation_depth": "deep",
                        "detail_density": "detailed",
                        "evidence_density": "high",
                    }
                },
            )
        )
        version = COPVersion(
            project_id=project.id,
            version_number=1,
            artifact_json=artifact.model_dump(mode="json"),
            change_summary="Imported validated LangChain reference COP",
            created_by="harness",
        )
        session.add(version)
        session.commit()
        print(f"Seeded project {project.id} with version {version.id} and its cited sources")


if __name__ == "__main__":
    main()
