"""Structured-output compatibility and failure classification.

A bare `json.loads` cannot tell a provider that ignores `response_format` from
one that hit its output limit. Both surfaced as the same error code, which made
the real cause invisible in the run history.
"""

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


def provider(handler) -> OpenAICompatibleProvider:
    return OpenAICompatibleProvider(
        base_url="https://provider.example/v1",
        api_key="test-key",
        model="test-model",
        max_retries=0,
        transport=httpx.MockTransport(handler),
    )


def respond(content: str, finish_reason: str | None = None) -> httpx.Response:
    message: dict[str, object] = {"content": content}
    choice: dict[str, object] = {"message": message}
    if finish_reason is not None:
        choice["finish_reason"] = finish_reason
    return httpx.Response(200, json={"choices": [choice]})


def generate(handler):
    return asyncio.run(
        provider(handler).generate_structured(
            system_prompt="system", user_prompt="user", schema=SCHEMA
        )
    )


def test_a_markdown_fenced_object_is_accepted_but_bare_prose_is_not():
    fenced = '```json\n{"goals":["ship"]}\n```'
    assert generate(lambda _request: respond(fenced)) == {"goals": ["ship"]}

    with pytest.raises(ProviderError) as error:
        generate(lambda _request: respond('Here you go: {"goals":["ship"]}'))
    assert error.value.code == "PROVIDER_INVALID_OUTPUT"


def test_a_truncated_response_is_reported_as_truncation_not_bad_json():
    with pytest.raises(ProviderError) as error:
        generate(lambda _request: respond('{"goals": ["sh', finish_reason="length"))

    assert error.value.code == "PROVIDER_OUTPUT_TRUNCATED"
    # Retrying the identical oversized request would burn the same budget again
    # and fail the same way; the run must fail once with an actionable message.
    assert error.value.retryable is False
    assert "output limit" in str(error.value)


def test_a_missing_message_is_distinguished_from_malformed_json():
    with pytest.raises(ProviderError) as error:
        generate(lambda _request: httpx.Response(200, json={"choices": []}))

    assert error.value.code == "PROVIDER_INVALID_OUTPUT"
    assert "did not contain a message" in str(error.value)


def test_a_json_array_is_not_accepted_as_the_contract_object():
    with pytest.raises(ProviderError):
        generate(lambda _request: respond('["goals"]'))


def test_schema_violations_still_name_the_failing_path():
    with pytest.raises(ProviderError) as error:
        generate(lambda _request: respond(json.dumps({"items": []})))

    assert "missing required field" in str(error.value)
    assert "$" in str(error.value)
