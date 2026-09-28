"""Stable error codes shared by the API and the Harness.

The wire format is `{"error": {"code", "message", "details"}}` per the API
contract. Codes must stay stable because the frontend maps them to recovery
actions.
"""

from typing import Any

from fastapi import HTTPException
from fastapi.responses import JSONResponse


class CopStudioError(Exception):
    """Base error carrying a stable code."""

    def __init__(
        self,
        code: str,
        message: str,
        *,
        status_code: int = 400,
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.status_code = status_code
        self.details = details or {}


class HarnessError(CopStudioError):
    """Raised when a Harness step cannot continue with the given context."""


class NotFoundError(CopStudioError):
    def __init__(self, message: str, *, code: str = "NOT_FOUND") -> None:
        super().__init__(code, message, status_code=404)


class ValidationFailure(CopStudioError):
    def __init__(
        self,
        message: str,
        *,
        code: str = "VALIDATION_ERROR",
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(code, message, status_code=422, details=details)


def error_body(code: str, message: str, details: dict[str, Any] | None = None) -> dict[str, Any]:
    return {"error": {"code": code, "message": message, "details": details or {}}}


def to_http_error(exc: CopStudioError) -> HTTPException:
    return HTTPException(
        status_code=exc.status_code,
        detail=error_body(exc.code, exc.message, exc.details),
    )


def error_response(exc: CopStudioError) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content=error_body(exc.code, exc.message, exc.details),
    )
