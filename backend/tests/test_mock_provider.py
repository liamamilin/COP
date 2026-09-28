import asyncio

import pytest

from app.harness.providers import MockProvider, ProviderError


def test_mock_provider_success_is_deterministic() -> None:
    provider = MockProvider()
    first = asyncio.run(
        provider.generate_structured(
            system_prompt="system", user_prompt="user", schema={"title": "T"}
        )
    )
    second = asyncio.run(
        provider.generate_structured(
            system_prompt="system", user_prompt="user", schema={"title": "T"}
        )
    )
    assert first == second


def test_mock_provider_exposes_rate_limit_failure() -> None:
    with pytest.raises(ProviderError, match="rate limited") as error:
        asyncio.run(MockProvider("rate_limit").health_check())
    assert error.value.code == "PROVIDER_RATE_LIMITED"
    assert error.value.retryable is True
