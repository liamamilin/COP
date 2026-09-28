import hashlib
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.db.models import Source, SourceDocument
from app.sources.extractors import SourceExtractionError, decode_text, extract_pdf, extract_url
from app.storage.local import LocalBlobStore


def get_blob_store() -> LocalBlobStore:
    return LocalBlobStore(get_settings().data_dir)


def process_source(db: Session, source: Source) -> SourceDocument | None:
    source.status = "processing"
    source.metadata_json = {
        key: value for key, value in source.metadata_json.items() if key != "error"
    }
    db.commit()
    try:
        if source.type == "url":
            if not source.original_uri:
                raise SourceExtractionError("The source URL is missing")
            text, extracted_metadata = extract_url(
                source.original_uri, get_settings().url_timeout_seconds
            )
            source.metadata_json = {**source.metadata_json, **extracted_metadata}
        else:
            if not source.blob_path:
                raise SourceExtractionError("The source file is missing")
            data = get_blob_store().get(source.blob_path)
            text = extract_pdf(data) if source.type == "pdf" else decode_text(data)

        document = db.scalar(select(SourceDocument).where(SourceDocument.source_id == source.id))
        if document is None:
            document = SourceDocument(
                source_id=source.id,
                content_hash=hashlib.sha256(text.encode()).hexdigest(),
            )
            db.add(document)
        document.text = text
        document.text_path = None
        document.content_hash = hashlib.sha256(text.encode()).hexdigest()
        document.char_count = len(text)
        document.metadata_json = {}
        source.status = "ready"
        db.commit()
        db.refresh(document)
        return document
    except (SourceExtractionError, OSError) as exc:
        source.status = "failed"
        source.metadata_json = {**source.metadata_json, "error": str(exc)}
        db.commit()
        return None


def safe_upload_name(filename: str | None, source_type: str) -> str:
    suffix = Path(filename or "").suffix.lower()
    expected = {"txt": ".txt", "markdown": ".md", "pdf": ".pdf"}[source_type]
    if source_type == "markdown" and suffix == ".markdown":
        return f"source{suffix}"
    if suffix != expected:
        raise SourceExtractionError(f"Expected a {expected} file")
    return f"source{suffix}"
