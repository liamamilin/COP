"""Persist web-research results as project Source snapshots.

The problem this solves: an artifact that cites `exa:9f2c...` while the
project's Source Manager is empty produces a citation the user cannot open. That
is worse than no citation, because it looks like evidence.

So a search result becomes a real `Source` row with a real `SourceDocument`,
using the same ids the run used. Everything a later step needs to re-open it --
url, title, bounded excerpt, fetch time, provider -- is stored, not just the text
the model happened to see.
"""

from __future__ import annotations

import hashlib
from datetime import UTC, datetime
from typing import Any
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import Source, SourceDocument

#: Ids the web adapter mints. Kept here so a reader can tell a persisted web
#: snapshot from a user-uploaded document without an extra column.
WEB_SOURCE_PREFIX = "exa:"


def snapshot_source_id(url: str) -> str:
    """The stable id for a URL, identical to the one Exa results carry.

    Deterministic on the URL alone, so re-running a search that finds the same
    page reuses the existing snapshot instead of accumulating duplicates.
    """
    return f"{WEB_SOURCE_PREFIX}{hashlib.sha256(url.encode('utf-8')).hexdigest()[:20]}"


def content_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def persist_search_results(
    db: Session,
    project_id: str | UUID,
    results: list[dict[str, Any]],
    *,
    provider: str = "exa",
) -> list[dict[str, Any]]:
    """Store each result as a project Source, reusing any existing snapshot.

    Idempotent by URL. A re-run that finds the same page updates the existing
    row's text in place rather than adding a second Source the user would have to
    recognise as a duplicate.
    """
    stored: list[dict[str, Any]] = []
    for result in results:
        url = str(result.get("original_uri") or result.get("url") or "").strip()
        if not url:
            # A result with no URL cannot be re-opened later, so persisting it
            # would create a citation that looks traceable and is not.
            continue
        text = str(result.get("text") or "").strip()
        title = str(result.get("title") or url).strip()
        source_id = result.get("id") or snapshot_source_id(url)
        fetched_at = datetime.now(UTC)

        source = db.scalar(
            select(Source).where(
                Source.project_id == project_id,
                Source.metadata_json["research_source_id"].astext == str(source_id),
            )
        )
        if source is None:
            source = Source(
                project_id=project_id,
                type="web_search",
                title=title[:300],
                original_uri=url,
                status="ready",
                metadata_json={
                    "provider": provider,
                    "research_source_id": str(source_id),
                    "fetched_at": fetched_at.isoformat(),
                },
            )
            db.add(source)
            db.flush()
            db.add(
                SourceDocument(
                    source_id=source.id,
                    text=text,
                    content_hash=content_hash(text),
                    char_count=len(text),
                )
            )
        else:
            source.title = title[:300]
            source.original_uri = url
            source.metadata_json = {
                **dict(source.metadata_json or {}),
                "provider": provider,
                "research_source_id": str(source_id),
                "fetched_at": fetched_at.isoformat(),
            }
            document = db.scalar(
                select(SourceDocument).where(SourceDocument.source_id == source.id)
            )
            if document is None:
                db.add(
                    SourceDocument(
                        source_id=source.id,
                        text=text,
                        content_hash=content_hash(text),
                        char_count=len(text),
                    )
                )
            else:
                document.text = text
                document.content_hash = content_hash(text)
                document.char_count = len(text)

        stored.append(
            {
                **result,
                # The persisted row is the authority. Reusing the adapter's id is
                # what lets H20/H30 keep a reference that the Source Manager can
                # resolve after a restart.
                "id": str(source_id),
                "title": title,
                "type": "web_search",
                "status": "ready",
                "text": text,
                "original_uri": url,
            }
        )
    db.commit()
    return stored


def research_source_ids(db: Session, project_id: str | UUID) -> set[str]:
    """Every research source id the project owns."""
    rows = db.scalars(select(Source).where(Source.project_id == project_id))
    return {
        str((row.metadata_json or {}).get("research_source_id"))
        for row in rows
        if (row.metadata_json or {}).get("research_source_id")
    }
