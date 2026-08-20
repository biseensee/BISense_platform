"""Async Redis client + a small caching decorator/helper for query results.

Used by the `dashboards` module to cache widget query results
(`QUERY_CACHE_TTL_SECONDS`, default 5 min) and can back rate limiting and
session/refresh-token denylists later. Kept thin and swappable behind
`CachePort` so use cases don't import `redis` directly.
"""
from __future__ import annotations

import hashlib
import json
from typing import Protocol

import orjson
from redis.asyncio import Redis

from src.config import Settings
from src.core.metrics import QUERY_CACHE_HITS_TOTAL, QUERY_CACHE_MISSES_TOTAL


class CachePort(Protocol):
    async def get_json(self, key: str) -> object | None: ...

    async def set_json(self, key: str, value: object, ttl_seconds: int) -> None: ...

    async def invalidate(self, key: str) -> None: ...

    async def invalidate_prefix(self, prefix: str) -> None: ...


class RedisCache:
    def __init__(self, settings: Settings) -> None:
        self._redis: Redis = Redis.from_url(settings.redis_url, decode_responses=False)

    async def get_json(self, key: str) -> object | None:
        raw = await self._redis.get(key)
        return orjson.loads(raw) if raw is not None else None

    async def set_json(self, key: str, value: object, ttl_seconds: int) -> None:
        await self._redis.set(key, orjson.dumps(value), ex=ttl_seconds)

    async def invalidate(self, key: str) -> None:
        await self._redis.delete(key)

    async def invalidate_prefix(self, prefix: str) -> None:
        # SCAN, not KEYS — never blocks the Redis event loop on large keyspaces.
        async for key in self._redis.scan_iter(match=f"{prefix}*", count=500):
            await self._redis.delete(key)

    async def close(self) -> None:
        await self._redis.aclose()


def build_query_cache_key(*, module: str, datasource_id: str, query_fingerprint: dict) -> str:
    """Deterministic cache key for a widget's data query.

    `query_fingerprint` should include everything that changes the result:
    the SQL/aggregation spec, filters, and applied row-level-security
    context (e.g. tenant id) — never just the widget id, or two tenants
    sharing a widget definition would leak each other's cached rows.
    """
    payload = json.dumps(query_fingerprint, sort_keys=True, default=str).encode()
    digest = hashlib.sha256(payload).hexdigest()[:32]
    return f"{module}:{datasource_id}:{digest}"


def record_cache_hit(module: str) -> None:
    QUERY_CACHE_HITS_TOTAL.labels(module=module).inc()


def record_cache_miss(module: str) -> None:
    QUERY_CACHE_MISSES_TOTAL.labels(module=module).inc()
