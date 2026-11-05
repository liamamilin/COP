import asyncio
import json
from typing import Any

import httpx
from jsonschema import Draft202012Validator

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
        transport: httpx.AsyncBaseTransport | None = None,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.model = model
        self.timeout = timeout
        self.max_retries = max_retries
        self.transport = transport

    def _headers(self) -> dict[str, str]:
        return {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}

    async def _request(self, method: str, path: str, **kwargs: Any) -> httpx.Response:
        for attempt in range(self.max_retries + 1):
            try:
                async with httpx.AsyncClient(
                    timeout=self.timeout, transport=self.transport
                ) as client:
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
                    if exc.retryable:
                        raise ProviderError(exc.code, str(exc), retryable=False) from exc
                    raise
            except httpx.TimeoutException as exc:
                if attempt >= self.max_retries:
                    raise ProviderError("PROVIDER_TIMEOUT", "Provider request timed out") from exc
            except httpx.HTTPError as exc:
                if attempt >= self.max_retries:
                    raise ProviderError(
                        "PROVIDER_UNAVAILABLE", "Provider endpoint is unavailable"
                    ) from exc
            await asyncio.sleep(0.15 * (attempt + 1))
        raise ProviderError("PROVIDER_UNAVAILABLE", "Provider endpoint is unavailable")

    async def _stream_completion(self, payload: dict[str, Any]) -> str:
        """Collect a streamed completion without a total-time read timeout.

        A non-streaming request sends nothing until the whole answer exists, so
        the read timeout applies to the entire generation. With a reasoning model
        that is routinely minutes, and every structured step failed as a timeout
        even though the provider was healthy. Streaming turns the timeout back
        into what it should be: a limit on silence between chunks.
        """
        body = {**payload, "stream": True}
        for attempt in range(self.max_retries + 1):
            collected: list[str] = []
            finish_reason: str | None = None
            try:
                async with (
                    httpx.AsyncClient(timeout=self.timeout, transport=self.transport) as client,
                    client.stream(
                        "POST",
                        f"{self.base_url}/chat/completions",
                        headers=self._headers(),
                        json=body,
                    ) as response,
                ):
                    if response.status_code in {401, 403}:
                        raise ProviderError("PROVIDER_AUTH_FAILED", "Provider rejected the API key")
                    if response.status_code == 429:
                        raise ProviderError(
                            "PROVIDER_RATE_LIMITED",
                            "Provider rate limit reached",
                            retryable=True,
                        )
                    response.raise_for_status()
                    if "text/event-stream" not in response.headers.get("content-type", ""):
                        # Some compatible endpoints ignore `stream`. Reading the
                        # ordinary body keeps them usable instead of failing on an
                        # empty stream.
                        body = json.loads(await response.aread())
                        try:
                            choice = body["choices"][0]
                        except (KeyError, IndexError, TypeError) as exc:
                            raise ProviderError(
                                "PROVIDER_INVALID_OUTPUT",
                                "Provider response did not contain a message",
                            ) from exc
                        finish_reason = choice.get("finish_reason")
                        content = (choice.get("message") or {}).get("content")
                        if finish_reason == "length":
                            raise ProviderError(
                                "PROVIDER_OUTPUT_TRUNCATED",
                                "Provider stopped at its output limit before finishing "
                                "the JSON. Reduce the request size or raise the "
                                "provider's output budget.",
                            )
                        if not isinstance(content, str):
                            raise ProviderError(
                                "PROVIDER_INVALID_OUTPUT",
                                "Provider response did not contain a message",
                            )
                        return content
                    async for line in response.aiter_lines():
                        if not line.startswith("data:"):
                            continue
                        data = line[len("data:") :].strip()
                        if data == "[DONE]":
                            break
                        try:
                            chunk = json.loads(data)
                        except json.JSONDecodeError:
                            continue
                        for choice in chunk.get("choices") or []:
                            delta = choice.get("delta") or {}
                            piece = delta.get("content")
                            if isinstance(piece, str):
                                collected.append(piece)
                            if choice.get("finish_reason"):
                                finish_reason = choice["finish_reason"]
                if finish_reason == "length":
                    raise ProviderError(
                        "PROVIDER_OUTPUT_TRUNCATED",
                        "Provider stopped at its output limit before finishing the JSON. "
                        "Reduce the request size or raise the provider's output budget.",
                    )
                return "".join(collected)
            except ProviderError as exc:
                if not exc.retryable or attempt >= self.max_retries:
                    if exc.retryable:
                        raise ProviderError(exc.code, str(exc), retryable=False) from exc
                    raise
            except httpx.TimeoutException as exc:
                if attempt >= self.max_retries:
                    raise ProviderError(
                        "PROVIDER_TIMEOUT",
                        "Provider stopped sending data for longer than the read timeout",
                    ) from exc
            except httpx.HTTPError as exc:
                if attempt >= self.max_retries:
                    raise ProviderError(
                        "PROVIDER_UNAVAILABLE", "Provider endpoint is unavailable"
                    ) from exc
            await asyncio.sleep(0.15 * (attempt + 1))
        raise ProviderError("PROVIDER_UNAVAILABLE", "Provider endpoint is unavailable")

    async def health_check(self) -> dict[str, Any]:
        response = await self._request("GET", "/models")
        return {"ok": True, "provider": "openai_compatible", "status": response.status_code}

    async def list_models(self) -> list[str]:
        """Return model IDs advertised by an OpenAI-compatible endpoint."""
        response = await self._request("GET", "/models")
        try:
            data = response.json()["data"]
            model_ids = sorted(
                {str(item["id"]).strip() for item in data if str(item.get("id", "")).strip()}
            )
        except (KeyError, TypeError, ValueError) as exc:
            raise ProviderError(
                "PROVIDER_INVALID_OUTPUT", "Provider returned an invalid model list"
            ) from exc
        if not model_ids:
            raise ProviderError("PROVIDER_INVALID_OUTPUT", "Provider returned no models")
        return model_ids

    async def generate_structured(
        self, *, system_prompt: str, user_prompt: str, schema: dict[str, Any]
    ) -> dict[str, Any]:
        schema_json = json.dumps(schema, ensure_ascii=False, separators=(",", ":"))
        structured_system_prompt = (
            f"{system_prompt}\n\n"
            "Return exactly one JSON object. Use the property names in the JSON Schema "
            "below and satisfy every required field. Do not add Markdown fences or prose.\n"
            f"JSON Schema:\n{schema_json}"
        )
        content = await self._stream_completion(
            {
                "model": self.model,
                "messages": [
                    {"role": "system", "content": structured_system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                "response_format": {"type": "json_object"},
            }
        )
        payload = self._parse_json_object(content)
        if payload is None:
            raise ProviderError(
                "PROVIDER_INVALID_OUTPUT", "Provider did not return valid structured JSON"
            )

        errors = sorted(
            Draft202012Validator(schema).iter_errors(payload),
            key=lambda error: list(error.absolute_path),
        )
        if errors:
            details = ", ".join(self._validation_detail(error) for error in errors[:3])
            contract = str(schema.get("title") or "structured output")
            raise ProviderError(
                "PROVIDER_INVALID_OUTPUT",
                f"Provider JSON does not satisfy {contract}: {details}",
            )
        return payload

    @staticmethod
    def _parse_json_object(content: Any) -> dict[str, Any] | None:
        """Accept a bare object or one wrapped in a Markdown code fence.

        Providers that ignore `response_format` commonly return ```json fences.
        Rejecting that would be a compatibility failure rather than a content
        failure, while accepting arbitrary prose would hide a real one, so only
        a fenced object or a bare object is accepted.
        """
        if not isinstance(content, str):
            return None
        text = content.strip()
        if text.startswith("```"):
            lines = text.splitlines()
            if len(lines) >= 2 and lines[-1].strip().startswith("```"):
                text = "\n".join(lines[1:-1]).strip()
        try:
            parsed = json.loads(text)
        except (json.JSONDecodeError, ValueError):
            # Trailing commentary is still prose; do not guess at a substring.
            return None
        return parsed if isinstance(parsed, dict) else None

    @staticmethod
    def _validation_detail(error: Any) -> str:
        path = "$" + "".join(
            f"[{part}]" if isinstance(part, int) else f".{part}" for part in error.absolute_path
        )
        if error.validator == "required" and isinstance(error.instance, dict):
            missing = [name for name in error.validator_value if name not in error.instance]
            return f"{path} missing required field(s) {', '.join(missing)}"
        if error.validator == "type":
            return f"{path} must be {error.validator_value}"
        return f"{path} failed the {error.validator} constraint"

    async def generate_text(self, *, system_prompt: str, user_prompt: str) -> str:
        return await self._stream_completion(
            {
                "model": self.model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
            }
        )
