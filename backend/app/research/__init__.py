"""Optional external research adapters."""

from app.research.exa import (
    ExaSearchClient,
    PersistResearch,
    enrich_context_with_web_search,
)
from app.research.snapshots import (
    WEB_SOURCE_PREFIX,
    persist_search_results,
    research_source_ids,
    snapshot_source_id,
)

__all__ = [
    "ExaSearchClient",
    "PersistResearch",
    "WEB_SOURCE_PREFIX",
    "enrich_context_with_web_search",
    "persist_search_results",
    "research_source_ids",
    "snapshot_source_id",
]
