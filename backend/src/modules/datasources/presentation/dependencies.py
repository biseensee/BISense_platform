from __future__ import annotations

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.config import Settings, get_settings
from src.core.dependencies import get_db_session, get_uow
from src.modules.datasources.application.use_cases import (
    CreateDataSourceUseCase,
    DeleteDataSourceUseCase,
    ListDataSourcesUseCase,
    TestDataSourceConnectionUseCase,
)
from src.modules.datasources.infrastructure.crypto import CredentialCipher
from src.modules.datasources.infrastructure.repositories import SqlAlchemyDataSourceRepository


def get_datasource_repository(
    session: AsyncSession = Depends(get_db_session),
) -> SqlAlchemyDataSourceRepository:
    return SqlAlchemyDataSourceRepository(session)


def get_credential_cipher(settings: Settings = Depends(get_settings)) -> CredentialCipher:
    return CredentialCipher(settings)


def get_create_datasource_use_case(
    repository: SqlAlchemyDataSourceRepository = Depends(get_datasource_repository),
    cipher: CredentialCipher = Depends(get_credential_cipher),
    uow=Depends(get_uow),
) -> CreateDataSourceUseCase:
    return CreateDataSourceUseCase(repository, cipher, uow)


def get_test_connection_use_case(
    repository: SqlAlchemyDataSourceRepository = Depends(get_datasource_repository),
    cipher: CredentialCipher = Depends(get_credential_cipher),
    uow=Depends(get_uow),
) -> TestDataSourceConnectionUseCase:
    return TestDataSourceConnectionUseCase(repository, cipher, uow)


def get_list_datasources_use_case(
    repository: SqlAlchemyDataSourceRepository = Depends(get_datasource_repository),
) -> ListDataSourcesUseCase:
    return ListDataSourcesUseCase(repository)


def get_delete_datasource_use_case(
    repository: SqlAlchemyDataSourceRepository = Depends(get_datasource_repository),
    uow=Depends(get_uow),
) -> DeleteDataSourceUseCase:
    return DeleteDataSourceUseCase(repository, uow)
