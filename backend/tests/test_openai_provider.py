import asyncio
import json

import httpx
import pytest

from app.harness.providers import OpenAICompatibleProvider, ProviderError

SCHEMA = {
    "title": "ExampleContract",
    "type": "object",
    "properties": {"goals": {"type": "array", "items": {"type": "string"}}},
    "required": ["goals"],
    "additionalProperties": True,
}


def provider_for(handler) -> OpenAICompatibleProvider:
    return OpenAICompatibleProvider(
        base_url="https://provider.example/v1",
        api_key="test-key",
        model="test-model",
        max_retries=0,
        transport=httpx.MockTransport(handler),
    )


def test_structured_generation_sends_schema_and_validates_response() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        body = json.loads(request.content)
        system_prompt = body["messages"][0]["content"]
        assert '"title":"ExampleContract"' in system_prompt
        assert '"required":["goals"]' in system_prompt
        assert body["response_format"] == {"type": "json_object"}
        return httpx.Response(
            200,
            json={"choices": [{"message": {"content": '{"goals":["ship"]}'}}]},
        )

    payload = asyncio.run(
        provider_for(handler).generate_structured(
            system_prompt="You are helpful.", user_prompt="Create goals.", schema=SCHEMA
        )
    )

    assert payload == {"goals": ["ship"]}


def test_structured_generation_rejects_json_that_misses_required_fields() -> None:
    def handler(_request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            json={"choices": [{"message": {"content": '{"items":[]}'}}]},
        )

    with pytest.raises(ProviderError, match="missing required field.*goals") as error:
        asyncio.run(
            provider_for(handler).generate_structured(
                system_prompt="system", user_prompt="user", schema=SCHEMA
            )
        )

    assert error.value.code == "PROVIDER_INVALID_OUTPUT"
