"""Handlers de exceção com respostas JSON consistentes."""

from __future__ import annotations

import logging

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from slowapi.errors import RateLimitExceeded
from starlette.exceptions import HTTPException as StarletteHTTPException

logger = logging.getLogger(__name__)


def _error_response(
    *,
    status_code: int,
    detail: str,
    code: str,
) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={"detail": detail, "code": code},
    )


def _format_validation_detail(exc: RequestValidationError) -> str:
    if not exc.errors():
        return "Dados de entrada inválidos."
    first = exc.errors()[0]
    loc = [str(part) for part in first.get("loc", []) if part != "body"]
    field = ".".join(loc) if loc else "entrada"
    message = first.get("msg", "valor inválido")
    return f"Campo '{field}': {message}"


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        _request: Request,
        exc: RequestValidationError,
    ) -> JSONResponse:
        return _error_response(
            status_code=422,
            detail=_format_validation_detail(exc),
            code="VALIDATION_ERROR",
        )

    @app.exception_handler(HTTPException)
    async def http_exception_handler(
        _request: Request,
        exc: HTTPException,
    ) -> JSONResponse:
        code = exc.headers.get("X-Error-Code") if exc.headers else None
        if not code:
            code = {
                400: "BAD_REQUEST",
                404: "NOT_FOUND",
                413: "PAYLOAD_TOO_LARGE",
                429: "RATE_LIMIT_EXCEEDED",
                500: "INTERNAL_ERROR",
            }.get(exc.status_code, "HTTP_ERROR")
        detail = exc.detail if isinstance(exc.detail, str) else str(exc.detail)
        return _error_response(status_code=exc.status_code, detail=detail, code=code)

    @app.exception_handler(StarletteHTTPException)
    async def starlette_http_exception_handler(
        _request: Request,
        exc: StarletteHTTPException,
    ) -> JSONResponse:
        detail = exc.detail if isinstance(exc.detail, str) else str(exc.detail)
        return _error_response(
            status_code=exc.status_code,
            detail=detail,
            code="HTTP_ERROR",
        )

    @app.exception_handler(RateLimitExceeded)
    async def rate_limit_handler(
        _request: Request,
        exc: RateLimitExceeded,
    ) -> JSONResponse:
        return _error_response(
            status_code=429,
            detail="Limite de requisições excedido. Tente novamente mais tarde.",
            code="RATE_LIMIT_EXCEEDED",
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(
        _request: Request,
        exc: Exception,
    ) -> JSONResponse:
        logger.exception("Erro interno não tratado: %s", exc)
        return _error_response(
            status_code=500,
            detail="Erro interno do servidor.",
            code="INTERNAL_ERROR",
        )
