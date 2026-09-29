import json

import httpx
import pytest

from app.core.errors import CopStudioError
from app.harness.context import HarnessContext
from app.harness.steps.h00_intake import MAX_SOURCE_EXCERPT
from app.research.exa import ExaSearchClient, enrich_context_with_web_search


def context() -> HarnessContext:
    return HarnessContext(
        run_id="run-1",
        project_id="project-1",
        input={
            "topic": "Reliable local knowledge work",
            "scope_hint": "Build a process-first learning artifact",
            "source_ids": [],
            "web_search": True,
        },
    )


@pytest.mark.asyncio
async def test_exa_results_become_bounded_untrusted_sources() -> None:
    async def handler(request: httpx.Request) -> httpx.Response:
        assert request.url == "https://api.exa.test/search"
        assert request.headers["x-api-key"] == "test-key"
        body = json.loads(request.content)
        assert body["numResults"] == 3
        assert body["contents"] == {"text": True}
        return httpx.Response(
            200,
            json={
                "results": [
                    {
                        "id": "result-1",
                        "title": "Process learning",
                        "url": "https://example.test/process",
                        "text": "x" * (MAX_SOURCE_EXCERPT + 100),
                    }
                ]
            },
        )

    ctx = context()
    count = await enrich_context_with_web_search(
        ctx,
        ExaSearchClient(
            api_key="test-key",
            base_url="https://api.exa.test",
            transport=httpx.MockTransport(handler),
        ),
        num_results=3,
    )

    assert count == 1
    assert ctx.source_bundle[0]["id"] == "exa:result-1"
    assert ctx.source_bundle[0]["type"] == "web_search"
    assert len(ctx.source_bundle[0]["text"]) == MAX_SOURCE_EXCERPT
    assert ctx.input["source_ids"] == ["exa:result-1"]


@pytest.mark.asyncio
async def test_checkpointed_search_results_are_not_fetched_twice() -> None:
    calls = 0

    async def handler(_request: httpx.Request) -> httpx.Response:
        nonlocal calls
        calls += 1
        return httpx.Response(
            200,
            json={"results": [{"id": "one", "title": "One", "url": "https://one.test"}]},
        )

    ctx = context()
    client = ExaSearchClient(
        api_key="test-key",
        base_url="https://api.exa.test",
        transport=httpx.MockTransport(handler),
    )
    assert await enrich_context_with_web_search(ctx, client) == 1
    assert await enrich_context_with_web_search(ctx, client) == 1
    assert calls == 1


@pytest.mark.asyncio
async def test_exa_auth_failure_has_an_actionable_code() -> None:
    async def handler(_request: httpx.Request) -> httpx.Response:
        return httpx.Response(401, json={"error": "invalid key"})

    client = ExaSearchClient(
        api_key="bad-key",
        base_url="https://api.exa.test",
        transport=httpx.MockTransport(handler),
    )
    with pytest.raises(CopStudioError) as error:
        await client.search("test")
    assert error.value.code == "SEARCH_AUTH_FAILED"
