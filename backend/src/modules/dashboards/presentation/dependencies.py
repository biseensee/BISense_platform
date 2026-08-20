from __future__ import annotations

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.config import Settings, get_settings
from src.core.cache import CachePort
from src.core.dependencies import get_cache, get_db_session, get_uow
from src.modules.dashboards.application.use_cases import (
    AddWidgetUseCase,
    CreateDashboardUseCase,
    DeleteDashboardUseCase,
    GetDashboardUseCase,
    GetWidgetDataUseCase,
    ListDashboardsUseCase,
)
from src.modules.dashboards.infrastructure.repositories import SqlAlchemyDashboardRepository
from src.modules.datasources.infrastructure.crypto import CredentialCipher
from src.modules.datasources.infrastructure.repositories import SqlAlchemyDataSourceRepository
from src.modules.datasources.presentation.dependencies import get_credential_cipher


def get_dashboard_repository(
    session: AsyncSession = Depends(get_db_session),
) -> SqlAlchemyDashboardRepository:
    return SqlAlchemyDashboardRepository(session)


def get_datasource_repository_for_dashboards(
    session: AsyncSession = Depends(get_db_session),
) -> SqlAlchemyDataSourceRepository:
    return SqlAlchemyDataSourceRepository(session)


def get_create_dashboard_use_case(
    repository: SqlAlchemyDashboardRepository = Depends(get_dashboard_repository),
    uow=Depends(get_uow),
) -> CreateDashboardUseCase:
    return CreateDashboardUseCase(repository, uow)


def get_add_widget_use_case(
    repository: SqlAlchemyDashboardRepository = Depends(get_dashboard_repository),
    uow=Depends(get_uow),
) -> AddWidgetUseCase:
    return AddWidgetUseCase(repository, uow)


def get_get_dashboard_use_case(
    repository: SqlAlchemyDashboardRepository = Depends(get_dashboard_repository),
) -> GetDashboardUseCase:
    return GetDashboardUseCase(repository)


def get_list_dashboards_use_case(
    repository: SqlAlchemyDashboardRepository = Depends(get_dashboard_repository),
) -> ListDashboardsUseCase:
    return ListDashboardsUseCase(repository)


def get_delete_dashboard_use_case(
    repository: SqlAlchemyDashboardRepository = Depends(get_dashboard_repository),
    uow=Depends(get_uow),
) -> DeleteDashboardUseCase:
    return DeleteDashboardUseCase(repository, uow)


def get_widget_data_use_case(
    dashboard_repository: SqlAlchemyDashboardRepository = Depends(get_dashboard_repository),
    datasource_repository: SqlAlchemyDataSourceRepository = Depends(
        get_datasource_repository_for_dashboards
    ),
    cipher: CredentialCipher = Depends(get_credential_cipher),
    cache: CachePort = Depends(get_cache),
    settings: Settings = Depends(get_settings),
) -> GetWidgetDataUseCase:
    return GetWidgetDataUseCase(
        dashboard_repository,
        datasource_repository,
        cipher,
        cache,
        settings.query_cache_ttl_seconds,
    )
