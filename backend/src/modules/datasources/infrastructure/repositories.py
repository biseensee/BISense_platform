from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.datasources.domain.entities import (
    ConnectionConfig,
    DataSource,
    DataSourceStatus,
    DataSourceType,
)
from src.modules.datasources.infrastructure.models import DataSourceModel


def _to_domain(row: DataSourceModel) -> DataSource:
    return DataSource(
        id=row.id,
        organization_id=row.organization_id,
        name=row.name,
        type=DataSourceType(row.type),
        config=ConnectionConfig(
            host=row.host,
            port=row.port,
            database=row.database_name,
            username=row.username,
            extra=row.extra,
        ),
        encrypted_credentials=row.encrypted_credentials,
        status=DataSourceStatus(row.status),
        last_connection_error=row.last_connection_error,
        created_by_user_id=row.created_by_user_id,
        created_at=row.created_at,
        updated_at=row.updated_at,
    )


def _to_row(ds: DataSource) -> DataSourceModel:
    return DataSourceModel(
        id=ds.id,
        organization_id=ds.organization_id,
        name=ds.name,
        type=ds.type.value,
        host=ds.config.host,
        port=ds.config.port,
        database_name=ds.config.database,
        username=ds.config.username,
        extra=ds.config.extra,
        encrypted_credentials=ds.encrypted_credentials,
        status=ds.status.value,
        last_connection_error=ds.last_connection_error,
        created_by_user_id=ds.created_by_user_id,
        created_at=ds.created_at,
        updated_at=ds.updated_at,
    )


class SqlAlchemyDataSourceRepository:
    """Implements `datasources.domain.repositories.DataSourceRepository`."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, datasource_id: uuid.UUID) -> DataSource | None:
        row = await self._session.get(DataSourceModel, datasource_id)
        return _to_domain(row) if row else None

    async def add(self, datasource: DataSource) -> None:
        self._session.add(_to_row(datasource))
        await self._session.flush()

    async def update(self, datasource: DataSource) -> None:
        row = await self._session.get(DataSourceModel, datasource.id)
        if row is None:
            return
        row.name = datasource.name
        row.status = datasource.status.value
        row.last_connection_error = datasource.last_connection_error
        row.encrypted_credentials = datasource.encrypted_credentials
        row.updated_at = datasource.updated_at
        await self._session.flush()

    async def delete(self, datasource: DataSource) -> None:
        row = await self._session.get(DataSourceModel, datasource.id)
        if row is not None:
            await self._session.delete(row)
            await self._session.flush()

    async def list_by_organization(self, organization_id: str) -> list[DataSource]:
        stmt = select(DataSourceModel).where(
            DataSourceModel.organization_id == organization_id
        )
        rows = (await self._session.execute(stmt)).scalars().all()
        return [_to_domain(r) for r in rows]
