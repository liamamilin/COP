import asyncio
import json
from typing import Any

import httpx

from app.harness.providers.base import ProviderError


class OpenAICompatibleProvider:
    def __init__(
        self,
        *,
        base_url: str,
        api_key: str,
        model: str,
        timeout: float = 60,
        max_retries: int = 2,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.model = model
        self.timeout = timeout
        self.max_retries = max_retries

    def _headers(self) -> dict[str, str]:
        return {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}

    async def _request(self, method: str, path: str, **kwargs: Any) -> httpx.Response:
        for attempt in range(self.max_retries + 1):
            try:
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    response = await client.request(
                        method, f"{self.base_url}{path}", headers=self._headers(), **kwargs
                    )
                if response.status_code in {401, 403}:
                    raise ProviderError("PROVIDER_AUTH_FAILED", "Provider rejected the API key")
                if response.status_code == 429:
                    raise ProviderError(
                        "PROVIDER_RATE_LIMITED", "Provider rate limit reached", retryable=True
                    )
                response.raise_for_status()
                return response
            except ProviderError as exc:
                if not exc.retryable or attempt >= self.max_retries:
                    raise
            except httpx.TimeoutException as exc:
                if attempt >= self.max_retries:
                    raise ProviderError(
                        "PROVIDER_TIMEOUT", "Provider request timed out", retryable=True
                    ) from exc
            except httpx.HTTPError as exc:
                if attempt >= self.max_retries:
                    raise ProviderError(
                        "PROVIDER_UNAVAILABLE", "Provider endpoint is unavailable", retryable=True
                    ) from exc
            await asyncio.sleep(0.15 * (attempt + 1))
        raise ProviderError("PROVIDER_UNAVAILABLE", "Provider endpoint is unavailable")

    async def health_check(self) -> dict[str, Any]:
        response = await self._request("GET", "/models")
        return {"ok": True, "provider": "openai_compatible", "status": response.status_code}

    async def generate_structured(
        self, *, system_prompt: str, user_prompt: str, schema: dict[str, Any]
    ) -> dict[str, Any]:
        response = await self._request(
            "POST",
            "/chat/completions",
            json={
                "model": self.model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                "response_format": {"type": "json_object"},
            },
        )
        try:
            content = response.json()["choices"][0]["message"]["content"]
            return json.loads(content)
        except (KeyError, IndexError, TypeError, json.JSONDecodeError) as exc:
            raise ProviderError(
                "PROVIDER_INVALID_OUTPUT", "Provider did not return valid structured JSON"
            ) from exc

    async def generate_text(self, *, system_prompt: str, user_prompt: str) -> str:
        response = await self._request(
            "POST",
            "/chat/completions",
            json={
                "model": self.model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
            },
        )
        try:
            return str(response.json()["choices"][0]["message"]["content"])
        except (KeyError, IndexError, TypeError) as exc:
            raise ProviderError(
                "PROVIDER_INVALID_OUTPUT", "Provider response is incomplete"
            ) from exc
