"""Optional external research adapters."""

from app.research.exa import ExaSearchClient, enrich_context_with_web_search

__all__ = ["ExaSearchClient", "enrich_context_with_web_search"]
