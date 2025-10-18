# Centralized exception handlers exposing a compact Problem+JSON error shape.

from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from pydantic import ValidationError


def problem(detail: str, status: int, type_: str = "about:blank") -> JSONResponse:
    return JSONResponse(status_code=status, content={"type": type_, "detail": detail, "status": status})


class NotFoundError(Exception):
    pass


class ConflictError(Exception):
    pass


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(ValidationError)
    async def handle_validation(_: Request, exc: ValidationError):
        return JSONResponse(status_code=422, content={"detail": exc.errors()})

    @app.exception_handler(NotFoundError)
    async def handle_not_found(_: Request, exc: NotFoundError):
        return problem(str(exc) or "Not found", 404)

    @app.exception_handler(ConflictError)
    async def handle_conflict(_: Request, exc: ConflictError):
        return problem(str(exc) or "Conflict", 409)

    @app.exception_handler(Exception)
    async def handle_generic(_: Request, exc: Exception):
        return problem("Internal Server Error", 500)


