"""PostgreSQL connector — for customer-owned Postgres warehouses (distinct
from the platform's own metadata Postgres in `core/database.py`).
"""
from __future__ import annotations

import asyncpg

from src.modules.datasources.domain.entities import ConnectionConfig
from src.modules.datasources.domain.exceptions import ConnectionTestFailedError
from src.modules.datasources.infrastructure.connectors.base import QueryResult, QuerySpec


class PostgresConnector:
    async def test_connection(
        self, config: ConnectionConfig, credentials: dict[str, str]
    ) -> None:
        try:
            conn = await asyncpg.connect(
                host=config.host,
                port=config.port,
                database=config.database,
                user=config.username,
                password=credentials.get("password", ""),
                timeout=5,
            )
            try:
                await conn.execute("SELECT 1")
            finally:
                await conn.close()
        except (OSError, asyncpg.PostgresError) as exc:
            raise ConnectionTestFailedError(str(exc)) from exc

    async def execute_query(
        self, config: ConnectionConfig, credentials: dict[str, str], spec: QuerySpec
    ) -> QueryResult:
        conn = await asyncpg.connect(
            host=config.host,
            port=config.port,
            database=config.database,
            user=config.username,
            password=credentials.get("password", ""),
            timeout=10,
        )
        try:
            # `spec.row_limit + 1` lets us detect truncation without a
            # separate COUNT(*) round trip.
            rows = await conn.fetch(
                f"{spec.sql} LIMIT {spec.row_limit + 1}", *spec.params.values()
            )
        finally:
            await conn.close()

        truncated = len(rows) > spec.row_limit
        rows = rows[: spec.row_limit]
        columns = list(rows[0].keys()) if rows else []
        return QueryResult(
            columns=columns,
            rows=[tuple(r.values()) for r in rows],
            truncated=truncated,
        )
