"""DataSource use cases. Connection secrets are encrypted before ever
reaching the repository/database — the application layer, not the ORM
model, owns that boundary so it's impossible to accidentally persist a
plaintext credential from a new code path.
"""
from __future__ import annotations

import uuid

from src.modules.datasources.application.dto import CreateDataSourceInput, DataSourceOutput
from src.modules.datasources.domain.entities import (
    ConnectionConfig,
    DataSource,
    DataSourceType,
)
from src.modules.datasources.domain.exceptions import DataSourceNotFoundError
from src.modules.datasources.domain.repositories import DataSourceRepository
from src.modules.datasources.infrastructure.connectors.registry import ConnectorRegistry
from src.modules.datasources.infrastructure.crypto import CredentialCipher
from src.shared.repository import UnitOfWorkProtocol


def _to_output(ds: DataSource) -> DataSourceOutput:
    return DataSourceOutput(
        id=str(ds.id),
        name=ds.name,
        type=ds.type.value,
        host=ds.config.host,
        port=ds.config.port,
        database=ds.config.database,
        username=ds.config.username,
        status=ds.status.value,
        last_connection_error=ds.last_connection_error,
    )


class CreateDataSourceUseCase:
    def __init__(
        self,
        repository: DataSourceRepository,
        cipher: CredentialCipher,
        uow: UnitOfWorkProtocol,
    ) -> None:
        self._repository = repository
        self._cipher = cipher
        self._uow = uow

    async def execute(self, data: CreateDataSourceInput) -> DataSourceOutput:
        datasource = DataSource(
            organization_id=data.organization_id,
            name=data.name,
            type=DataSourceType(data.type),
            config=ConnectionConfig(
                host=data.host,
                port=data.port,
                database=data.database,
                username=data.username,
                extra=data.extra,
            ),
            encrypted_credentials=self._cipher.encrypt(data.credentials),
            created_by_user_id=data.created_by_user_id,
        )
        async with self._uow:
            await self._repository.add(datasource)
            await self._uow.commit()
        return _to_output(datasource)


class TestDataSourceConnectionUseCase:
    """Verifies connectivity and persists the resulting status — so the UI
    can show a green/red indicator without re-testing on every page load.
    """

    def __init__(
        self,
        repository: DataSourceRepository,
        cipher: CredentialCipher,
        uow: UnitOfWorkProtocol,
    ) -> None:
        self._repository = repository
        self._cipher = cipher
        self._uow = uow

    async def execute(self, datasource_id: uuid.UUID) -> DataSourceOutput:
        datasource = await self._repository.get_by_id(datasource_id)
        if datasource is None:
            raise DataSourceNotFoundError(datasource_id)

        connector = ConnectorRegistry.get(datasource.type)
        credentials = self._cipher.decrypt(datasource.encrypted_credentials)
        try:
            await connector.test_connection(datasource.config, credentials)
        except Exception as exc:  # noqa: BLE001 - normalized into domain status
            datasource.mark_error(str(exc))
        else:
            datasource.mark_connected()

        async with self._uow:
            await self._repository.update(datasource)
            await self._uow.commit()
        return _to_output(datasource)


class ListDataSourcesUseCase:
    def __init__(self, repository: DataSourceRepository) -> None:
        self._repository = repository

    async def execute(self, organization_id: str) -> list[DataSourceOutput]:
        items = await self._repository.list_by_organization(organization_id)
        return [_to_output(i) for i in items]


class DeleteDataSourceUseCase:
    def __init__(self, repository: DataSourceRepository, uow: UnitOfWorkProtocol) -> None:
        self._repository = repository
        self._uow = uow

    async def execute(self, datasource_id: uuid.UUID) -> None:
        datasource = await self._repository.get_by_id(datasource_id)
        if datasource is None:
            raise DataSourceNotFoundError(datasource_id)
        async with self._uow:
            await self._repository.delete(datasource)
            await self._uow.commit()
