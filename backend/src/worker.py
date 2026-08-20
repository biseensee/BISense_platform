"""Background worker process (arq) — scheduled cache warmups and async jobs
that shouldn't run inline in a request/response cycle (e.g. refreshing a
popular dashboard's widget cache before it expires, so viewers never hit a
cold-cache query against a multi-TB warehouse).

Run with: `arq src.worker.WorkerSettings`
"""
from __future__ import annotations

from arq import cron
from arq.connections import RedisSettings

from src.config import get_settings
from src.core.logging import configure_logging, get_logger

logger = get_logger(__name__)


async def startup(ctx: dict) -> None:
    configure_logging()
    logger.info("worker_startup")


async def shutdown(ctx: dict) -> None:
    logger.info("worker_shutdown")


async def warm_dashboard_cache(ctx: dict, dashboard_id: str) -> None:
    """Placeholder job: pre-executes every widget on a dashboard so its
    cache entry never goes cold for viewers. Wire up with
    `GetWidgetDataUseCase` per widget once a job-scheduling API exists for
    "pin this dashboard's refresh cadence" (natural extension point).
    """
    logger.info("warm_dashboard_cache", dashboard_id=dashboard_id)


async def refresh_all_pinned_dashboards(ctx: dict) -> None:
    """Cron entry point — iterate dashboards flagged for scheduled refresh."""
    logger.info("refresh_all_pinned_dashboards_tick")


class WorkerSettings:
    functions = [warm_dashboard_cache]
    cron_jobs = [cron(refresh_all_pinned_dashboards, minute=set(range(0, 60, 5)))]
    on_startup = startup
    on_shutdown = shutdown
    redis_settings = RedisSettings.from_dsn(get_settings().redis_url)
