"""ClickHouse connector — the recommended target for multi-TB analytical
datasets (columnar storage, high compression, sub-second aggregation over
billions of rows), where a row-store Postgres warehouse would not scale.
"""
from __future__ import annotations

import asyncio

import clickhouse_connect

from src.modules.datasources.domain.entities import ConnectionConfig
from src.modules.datasources.domain.exceptions import ConnectionTestFailedError
from src.modules.datasources.infrastructure.connectors.base import QueryResult, QuerySpec


class ClickHouseConnector:
    """`clickhouse-connect` is sync, so calls are offloaded to a thread via
    `asyncio.to_thread` to avoid blocking the event loop — a pragmatic
    bridge until an async-native client is adopted.
    """

    async def test_connection(
        self, config: ConnectionConfig, credentials: dict[str, str]
    ) -> None:
        try:
            await asyncio.to_thread(self._ping, config, credentials)
        except Exception as exc:
            raise ConnectionTestFailedError(str(exc)) from exc

    def _ping(self, config: ConnectionConfig, credentials: dict[str, str]) -> None:
        client = clickhouse_connect.get_client(
            host=config.host,
            port=config.port,
            database=config.database,
            username=config.username,
            password=credentials.get("password", ""),
            connect_timeout=5,
        )
        client.command("SELECT 1")

    async def execute_query(
        self, config: ConnectionConfig, credentials: dict[str, str], spec: QuerySpec
    ) -> QueryResult:
        return await asyncio.to_thread(self._run_query, config, credentials, spec)

    def _run_query(
        self, config: ConnectionConfig, credentials: dict[str, str], spec: QuerySpec
    ) -> QueryResult:
        client = clickhouse_connect.get_client(
            host=config.host,
            port=config.port,
            database=config.database,
            username=config.username,
            password=credentials.get("password", ""),
        )
        result = client.query(
            f"{spec.sql} LIMIT {spec.row_limit + 1}", parameters=spec.params
        )
        rows = result.result_rows
        truncated = len(rows) > spec.row_limit
        return QueryResult(
            columns=list(result.column_names),
            rows=rows[: spec.row_limit],
            truncated=truncated,
        )
