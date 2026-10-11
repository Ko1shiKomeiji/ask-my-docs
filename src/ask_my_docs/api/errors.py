from collections.abc import Mapping
from typing import Any

import structlog
from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from ask_my_docs.core.errors import AppError, BadRequestError, ConflictError, NotFoundError
from ask_my_docs.core.middleware import REQUEST_ID_HEADER

logger = structlog.get_logger()

_STATUS_BY_ERROR: dict[type[AppError], int] = {
    NotFoundError: status.HTTP_404_NOT_FOUND,
    BadRequestError: status.HTTP_400_BAD_REQUEST,
    ConflictError: status.HTTP_409_CONFLICT,
}


def _status_for(exc: AppError) -> int:
    for cls in type(exc).__mro__:
        if cls in _STATUS_BY_ERROR:
            return _STATUS_BY_ERROR[cls]

    return status.HTTP_500_INTERNAL_SERVER_ERROR


def _error_response(
    status_code: int,
    code: str,
    message: str,
    *,
    headers: Mapping[str, str] | None = None,
    details: list[Any] | None = None,
) -> JSONResponse:
    body: dict[str, Any] = {"code": code, "message": message}
    if details is not None:
        body["details"] = details

    return JSONResponse(status_code=status_code, content={"error": body}, headers=headers)


async def _app_error_handler(request: Request, exc: AppError) -> JSONResponse:
    status_code = _status_for(exc)
    logger.warning("app_error", status_code=status_code, code=exc.code, msg=exc.message)
    return _error_response(status_code, exc.code, exc.message)


async def _http_error_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    code = "not_found" if exc.status_code == 404 else "http_error"
    logger.info("http_error", status_code=exc.status_code, code=code, msg=exc.detail)
    return _error_response(exc.status_code, code, str(exc.detail), headers=exc.headers)


async def _validation_error_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    # без поля "input": в нём сырые данные клиента, им не место ни в логах, ни в ответе
    details = [{"loc": e["loc"], "msg": e["msg"]} for e in exc.errors()]
    logger.info("validation_error", errors=details)
    return _error_response(
        status.HTTP_422_UNPROCESSABLE_CONTENT,
        "validation_error",
        "Request validation failed",
        details=details,
    )


async def _unhandled_error_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.exception("unhandled_error", path=request.url.path)
    request_id = structlog.contextvars.get_contextvars().get("request_id")
    headers = {REQUEST_ID_HEADER: request_id} if request_id is not None else None
    return _error_response(
        status.HTTP_500_INTERNAL_SERVER_ERROR, "internal", "Internal Server Error", headers=headers
    )


def register_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(AppError, _app_error_handler)  # type: ignore[arg-type]
    app.add_exception_handler(StarletteHTTPException, _http_error_handler)  # type: ignore[arg-type]
    app.add_exception_handler(RequestValidationError, _validation_error_handler)  # type: ignore[arg-type]
    app.add_exception_handler(Exception, _unhandled_error_handler)
