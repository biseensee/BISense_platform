from __future__ import annotations

from pydantic import BaseModel, Field


class CreateDataSourceRequest(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    type: str = Field(description="postgresql | clickhouse | mysql | csv_upload")
    host: str
    port: int
    database: str
    username: str
    credentials: dict[str, str] = Field(
        default_factory=dict, description="Secret fields (e.g. password) — encrypted at rest"
    )
    extra: dict[str, str] = Field(default_factory=dict)


class DataSourceResponse(BaseModel):
    id: str
    name: str
    type: str
    host: str
    port: int
    database: str
    username: str
    status: str
    last_connection_error: str | None
