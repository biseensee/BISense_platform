"""Connector protocol every data-warehouse driver implements.

`dashboards` module's query-execution use case depends on this interface
(`Connector`), resolved via `ConnectorRegistry.get(datasource.type)` — it
never imports a concrete driver (psycopg/clickhouse-connect) directly, so
adding a new warehouse type means adding one file here plus a registry entry.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol

from src.modules.datasources.domain.entities import ConnectionConfig


@dataclass(frozen=True, slots=True)
class QuerySpec:
    """A vetted, parameterized query — never raw string-concatenated SQL.

    `sql` must use driver-native placeholders; `params` are bound values.
    The application layer is responsible for building this from a widget's
    declarative aggregation spec (dimension/measure/filter), which keeps
    arbitrary SQL injection out of the trust boundary between end users and
    the connector.
    """

    sql: str
    params: dict[str, Any]
    row_limit: int = 10_000


@dataclass(frozen=True, slots=True)
class QueryResult:
    columns: list[str]
    rows: list[tuple[Any, ...]]
    truncated: bool  # True if row_limit was hit


class Connector(Protocol):
    """One instance per (datasource, request) — connectors are cheap
    context-managed clients, not long-lived pooled singletons; pooling is
    the driver library's job (e.g. asyncpg.Pool) managed by the registry.
    """

    async def test_connection(
        self, config: ConnectionConfig, credentials: dict[str, str]
    ) -> None:
        """Raises `ConnectionTestFailedError` on failure; returns None on success."""
        ...

    async def execute_query(
        self, config: ConnectionConfig, credentials: dict[str, str], spec: QuerySpec
    ) -> QueryResult: ...
