"""Cross-cutting HTTP middleware: request-id correlation + metrics + timing."""
from __future__ import annotations

import time
import uuid
from collections.abc import Awaitable, Callable

import structlog
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from src.core.metrics import HTTP_REQUEST_DURATION_SECONDS, HTTP_REQUESTS_TOTAL

RequestResponseEndpoint = Callable[[Request], Awaitable[Response]]


class RequestContextMiddleware(BaseHTTPMiddleware):
    """Binds a `request_id` to structlog contextvars and records metrics.

    A route's `path` template (not the raw URL, which would blow up metric
    cardinality with path params like `/dashboards/{id}`) is pulled from
    `request.scope["route"]` after routing has resolved.
    """

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        request_id = request.headers.get("x-request-id", str(uuid.uuid4()))
        structlog.contextvars.clear_contextvars()
        structlog.contextvars.bind_contextvars(request_id=request_id)

        start = time.perf_counter()
        response = await call_next(request)
        duration = time.perf_counter() - start

        route = request.scope.get("route")
        path_template = getattr(route, "path", request.url.path)

        HTTP_REQUESTS_TOTAL.labels(
            method=request.method, path=path_template, status_code=response.status_code
        ).inc()
        HTTP_REQUEST_DURATION_SECONDS.labels(
            method=request.method, path=path_template
        ).observe(duration)

        response.headers["x-request-id"] = request_id
        return response
