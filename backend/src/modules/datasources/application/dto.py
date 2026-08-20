from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True, slots=True)
class CreateDataSourceInput:
    organization_id: str
    created_by_user_id: str
    name: str
    type: str
    host: str
    port: int
    database: str
    username: str
    credentials: dict[str, str] = field(default_factory=dict)
    extra: dict[str, str] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class DataSourceOutput:
    id: str
    name: str
    type: str
    host: str
    port: int
    database: str
    username: str
    status: str
    last_connection_error: str | None
