"""Translates domain exceptions into consistent JSON error responses.

Registered once in `main.py`. Keeping this in `core` (presentation-adjacent)
means domain/application code never imports FastAPI — see `core/exceptions.py`.
"""
from __future__ import annotations

import structlog
from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from src.core.exceptions import DomainError

logger = structlog.get_logger(__name__)


def _error_body(code: str, message: str, details: dict | None = None) -> dict:
    return {"error": {"code": code, "message": message, "details": details or {}}}


def register_error_handlers(app: FastAPI) -> None:
    @app.exception_handler(DomainError)
    async def handle_domain_error(request: Request, exc: DomainError) -> JSONResponse:
        logger.info(
            "domain_error", code=exc.code, message=exc.message, path=request.url.path
        )
        return JSONResponse(
            status_code=exc.http_status,
            content=_error_body(exc.code, exc.message, exc.details),
        )

    @app.exception_handler(RequestValidationError)
    async def handle_validation_error(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=_error_body(
                "request_validation_error", "Invalid request payload", {"errors": exc.errors()}
            ),
        )

    @app.exception_handler(Exception)
    async def handle_unexpected_error(request: Request, exc: Exception) -> JSONResponse:
        logger.error(
            "unhandled_exception", error=str(exc), path=request.url.path, exc_info=True
        )
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=_error_body("internal_error", "An unexpected error occurred"),
        )
