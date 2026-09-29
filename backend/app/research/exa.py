"""Exa-backed web research for an explicitly opted-in generation run.

Search results become ordinary untrusted source excerpts. The Harness prompt
already treats every source as data rather than instructions, so web content
cannot override the system prompt or schema contract.
"""

import hashlib
from typing import Any

import httpx

from app.core.errors import CopStudioError
from app.harness.context import HarnessContext
from app.harness.steps.h00_intake import MAX_SOURCE_EXCERPT


class ExaSearchClient:
    def __init__(
        self,
        *,
        api_key: str,
        base_url: str = "https://api.exa.ai",
        timeout: float = 30,
        transport: httpx.AsyncBaseTransport | None = None,
    ) -> None:
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.transport = transport

    async def search(self, query: str, *, num_results: int = 5) -> list[dict[str, Any]]:
        """Return bounded source excerpts from Exa's official search endpoint."""
        try:
            async with httpx.AsyncClient(
                timeout=self.timeout,
                transport=self.transport,
            ) as client:
                response = await client.post(
                    f"{self.base_url}/search",
                    headers={"x-api-key": self.api_key, "Content-Type": "application/json"},
                    json={
                        "query": query,
                        "numResults": max(1, min(num_results, 10)),
                        "type": "auto",
                        "contents": {"text": True},
                    },
                )
        except httpx.TimeoutException as exc:
            raise CopStudioError(
                "SEARCH_TIMEOUT",
                "Exa search timed out. Retry the run or disable web research.",
                status_code=503,
            ) from exc
        except httpx.HTTPError as exc:
            raise CopStudioError(
                "SEARCH_UNAVAILABLE",
                "Exa search is unavailable. Retry the run or disable web research.",
                status_code=503,
            ) from exc

        if response.status_code in {401, 403}:
            raise CopStudioError(
                "SEARCH_AUTH_FAILED",
                "Exa rejected the configured API key.",
                status_code=401,
            )
        if response.status_code == 429:
            raise CopStudioError(
                "SEARCH_RATE_LIMITED",
                "Exa rate limit reached. Retry later or disable web research.",
                status_code=429,
            )
        try:
            response.raise_for_status()
            payload = response.json()
        except (httpx.HTTPError, ValueError) as exc:
            raise CopStudioError(
                "SEARCH_INVALID_RESPONSE",
                "Exa returned an invalid search response.",
                status_code=502,
            ) from exc

        sources: list[dict[str, Any]] = []
        for result in payload.get("results") or []:
            if not isinstance(result, dict):
                continue
            url = str(result.get("url") or "").strip()
            title = str(result.get("title") or url or "Untitled web result").strip()
            text = str(result.get("text") or result.get("summary") or "").strip()
            if not text:
                text = f"{title}\n{url}".strip()
            raw_id = str(result.get("id") or "").strip()
            stable_id = raw_id or hashlib.sha256(url.encode("utf-8")).hexdigest()[:20]
            sources.append(
                {
                    "id": f"exa:{stable_id}",
                    "title": title,
                    "type": "web_search",
                    "status": "ready",
                    "text": text[:MAX_SOURCE_EXCERPT],
                    "original_uri": url,
                }
            )
        return sources


def search_query(context: HarnessContext) -> str:
    topic = str(context.input.get("topic") or "").strip()
    scope = str(context.input.get("scope_hint") or "").strip()
    return " — ".join(item for item in (topic, scope) if item)


async def enrich_context_with_web_search(
    context: HarnessContext,
    client: ExaSearchClient,
    *,
    num_results: int = 5,
) -> int:
    """Attach Exa results once and make H00 include their synthetic ids."""
    existing = [item for item in context.source_bundle if item.get("type") == "web_search"]
    if existing:
        return len(existing)

    query = search_query(context)
    if not query:
        return 0
    results = await client.search(query, num_results=num_results)
    context.source_bundle.extend(results)
    selected_ids = list(context.input.get("source_ids") or [])
    for result in results:
        if result["id"] not in selected_ids:
            selected_ids.append(result["id"])
    context.input["source_ids"] = selected_ids
    return len(results)
