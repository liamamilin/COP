from typing import Any, Protocol


class ProviderError(RuntimeError):
    def __init__(self, code: str, message: str, *, retryable: bool = False) -> None:
        super().__init__(message)
        self.code = code
        self.retryable = retryable


class LLMProvider(Protocol):
    async def health_check(self) -> dict[str, Any]: ...

    async def generate_structured(
        self, *, system_prompt: str, user_prompt: str, schema: dict[str, Any]
    ) -> dict[str, Any]: ...

    async def generate_text(self, *, system_prompt: str, user_prompt: str) -> str: ...
