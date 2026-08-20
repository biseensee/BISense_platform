"""Application entrypoint / composition root.

`create_app()` is the only place that wires concrete infrastructure
(SQLAlchemy engine, Redis client, JWT service) into the FastAPI app and
mounts each module's presentation router. Modules never import each other's
internals — only their public router + schemas — so a module can be pulled
out into its own service later with minimal churn.
"""
from __future__ import annotations

from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest
from starlette.responses import Response

from src.config import get_settings
from src.core.cache import RedisCache
from src.core.database import Database
from src.core.error_handlers import register_error_handlers
from src.core.logging import configure_logging, get_logger
from src.core.middleware import RequestContextMiddleware
from src.modules.auth.presentation.router import router as auth_router
from src.modules.dashboards.presentation.router import router as dashboards_router
from src.modules.datasources.presentation.router import router as datasources_router

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    settings = get_settings()
    configure_logging()

    database = Database(settings)
    cache = RedisCache(settings)
    app.state.database = database
    app.state.cache = cache

    logger.info("app_startup", app_env=settings.app_env)
    yield

    await cache.close()
    await database.dispose()
    logger.info("app_shutdown")


def create_app() -> FastAPI:
    settings = get_settings()

    app = FastAPI(
        title=settings.app_name,
        description=(
            "Enterprise BI platform API — dashboards, data sources, and "
            "authentication. See /docs for interactive OpenAPI documentation."
        ),
        version="0.1.0",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.backend_cors_origins or ["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_middleware(RequestContextMiddleware)

    register_error_handlers(app)

    app.include_router(auth_router, prefix=settings.api_prefix)
    app.include_router(datasources_router, prefix=settings.api_prefix)
    app.include_router(dashboards_router, prefix=settings.api_prefix)

    @app.get("/healthz", tags=["system"], summary="Liveness probe")
    async def healthz() -> dict[str, str]:
        return {"status": "ok"}

    @app.get(settings.prometheus_metrics_path, tags=["system"], summary="Prometheus metrics")
    async def metrics() -> Response:
        return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

    return app


app = create_app()
