from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, status

from src.modules.auth.domain.entities import Permission, User
from src.modules.auth.presentation.dependencies import RequirePermission
from src.modules.datasources.application.dto import CreateDataSourceInput
from src.modules.datasources.application.use_cases import (
    CreateDataSourceUseCase,
    DeleteDataSourceUseCase,
    ListDataSourcesUseCase,
    TestDataSourceConnectionUseCase,
)
from src.modules.datasources.presentation.dependencies import (
    get_create_datasource_use_case,
    get_delete_datasource_use_case,
    get_list_datasources_use_case,
    get_test_connection_use_case,
)
from src.modules.datasources.presentation.schemas import (
    CreateDataSourceRequest,
    DataSourceResponse,
)

router = APIRouter(prefix="/datasources", tags=["datasources"])


@router.post(
    "",
    response_model=DataSourceResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new data source",
    description=(
        "Stores connection metadata for an external warehouse. Secret "
        "fields in `credentials` (e.g. `password`) are encrypted at rest "
        "with Fernet and never returned by any endpoint. Connectivity is "
        "not verified automatically — call `POST /{id}/test-connection`."
    ),
)
async def create_datasource(
    body: CreateDataSourceRequest,
    user: User = Depends(RequirePermission(Permission.DATASOURCE_CREATE)),
    use_case: CreateDataSourceUseCase = Depends(get_create_datasource_use_case),
) -> DataSourceResponse:
    output = await use_case.execute(
        CreateDataSourceInput(
            organization_id=user.organization_id,
            created_by_user_id=str(user.id),
            name=body.name,
            type=body.type,
            host=body.host,
            port=body.port,
            database=body.database,
            username=body.username,
            credentials=body.credentials,
            extra=body.extra,
        )
    )
    return DataSourceResponse(**output.__dict__)


@router.post(
    "/{datasource_id}/test-connection",
    response_model=DataSourceResponse,
    summary="Test connectivity and refresh the data source's health status",
)
async def test_connection(
    datasource_id: uuid.UUID,
    user: User = Depends(RequirePermission(Permission.DATASOURCE_EDIT)),
    use_case: TestDataSourceConnectionUseCase = Depends(get_test_connection_use_case),
) -> DataSourceResponse:
    output = await use_case.execute(datasource_id)
    return DataSourceResponse(**output.__dict__)


@router.get(
    "",
    response_model=list[DataSourceResponse],
    summary="List data sources visible to the current organization",
)
async def list_datasources(
    user: User = Depends(RequirePermission(Permission.DATASOURCE_VIEW)),
    use_case: ListDataSourcesUseCase = Depends(get_list_datasources_use_case),
) -> list[DataSourceResponse]:
    items = await use_case.execute(user.organization_id)
    return [DataSourceResponse(**i.__dict__) for i in items]


@router.delete(
    "/{datasource_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a data source",
)
async def delete_datasource(
    datasource_id: uuid.UUID,
    user: User = Depends(RequirePermission(Permission.DATASOURCE_DELETE)),
    use_case: DeleteDataSourceUseCase = Depends(get_delete_datasource_use_case),
) -> None:
    await use_case.execute(datasource_id)
