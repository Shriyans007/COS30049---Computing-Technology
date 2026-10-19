"""Consistent client-safe API errors."""

import logging

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException


LOGGER = logging.getLogger("a3.api")


class AppError(Exception):
    def __init__(self, status_code: int, code: str, message: str) -> None:
        self.status_code = status_code
        self.code = code
        self.message = message
        super().__init__(message)


def error_payload(code: str, message: str) -> dict[str, dict[str, str]]:
    return {"error": {"code": code, "message": message}}


def install_error_handlers(app: FastAPI) -> None:
    @app.exception_handler(AppError)
    async def app_error_handler(_: Request, error: AppError) -> JSONResponse:
        return JSONResponse(error_payload(error.code, error.message), status_code=error.status_code)

    @app.exception_handler(RequestValidationError)
    async def validation_error_handler(_: Request, __: RequestValidationError) -> JSONResponse:
        return JSONResponse(
            error_payload("INVALID_REQUEST", "The request body is malformed or has invalid fields."),
            status_code=422,
        )

    @app.exception_handler(StarletteHTTPException)
    async def http_error_handler(_: Request, error: StarletteHTTPException) -> JSONResponse:
        code = "NOT_FOUND" if error.status_code == 404 else "HTTP_ERROR"
        message = "The requested API resource does not exist." if error.status_code == 404 else "The request could not be completed."
        return JSONResponse(error_payload(code, message), status_code=error.status_code)

    @app.exception_handler(Exception)
    async def unexpected_error_handler(request: Request, error: Exception) -> JSONResponse:
        LOGGER.exception("Unexpected error for %s %s", request.method, request.url.path, exc_info=error)
        return JSONResponse(
            error_payload("INTERNAL_ERROR", "An unexpected server error occurred."),
            status_code=500,
        )
