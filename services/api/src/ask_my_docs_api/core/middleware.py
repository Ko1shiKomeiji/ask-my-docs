import re
import time
import uuid

import structlog
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

_REQUEST_ID_RE = re.compile(r"[A-Za-z0-9\-_]{1,64}")
REQUEST_ID_HEADER = "X-Request-ID"

logger = structlog.get_logger()


class RequestIDMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        structlog.contextvars.clear_contextvars()
        request_id = request.headers.get(REQUEST_ID_HEADER)
        if request_id is None or not _REQUEST_ID_RE.fullmatch(request_id):
            request_id = str(uuid.uuid4())
        structlog.contextvars.bind_contextvars(request_id=request_id)

        start = time.perf_counter()
        # если call_next выбросит исключение, ответ сформирует обработчик 500 снаружи
        status_code = 500
        try:
            response = await call_next(request)
            status_code = response.status_code
        finally:
            logger.info(
                "request",
                method=request.method,
                path=request.url.path,
                status_code=status_code,
                duration_ms=round((time.perf_counter() - start) * 1000, 1),
            )

        response.headers[REQUEST_ID_HEADER] = request_id
        return response
