"""DataSource domain: the metadata + connection config for an external
data warehouse/DB the platform queries at dashboard-render time.

Connection secrets (`credentials`) are stored encrypted at rest (see
`infrastructure/crypto.py`) and are never logged or included in `__repr__`.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum

from src.shared.domain import AggregateRoot


class DataSourceType(StrEnum):
    POSTGRESQL = "postgresql"
    CLICKHOUSE = "clickhouse"
    MYSQL = "mysql"
    CSV_UPLOAD = "csv_upload"


class DataSourceStatus(StrEnum):
    PENDING = "pending"        # created, connection not yet verified
    CONNECTED = "connected"
    ERROR = "error"


@dataclass(kw_only=True)
class ConnectionConfig:
    """Non-secret connection parameters. Secrets (password, API key) are
    kept separately in `DataSource.encrypted_credentials` so this object is
    safe to include in logs/audit trails.
    """

    host: str
    port: int
    database: str
    username: str
    extra: dict[str, str] = field(default_factory=dict)  # e.g. sslmode, schema


@dataclass(kw_only=True)
class DataSource(AggregateRoot):
    organization_id: str
    name: str
    type: DataSourceType
    config: ConnectionConfig
    encrypted_credentials: bytes = field(repr=False)
    status: DataSourceStatus = DataSourceStatus.PENDING
    last_connection_error: str | None = None
    created_by_user_id: str = ""

    def mark_connected(self) -> None:
        self.status = DataSourceStatus.CONNECTED
        self.last_connection_error = None
        self.touch()

    def mark_error(self, message: str) -> None:
        self.status = DataSourceStatus.ERROR
        self.last_connection_error = message
        self.touch()
