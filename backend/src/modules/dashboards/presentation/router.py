from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, status

from src.modules.auth.domain.entities import Permission, User
from src.modules.auth.presentation.dependencies import RequirePermission
from src.modules.dashboards.application.dto import AddWidgetInput, CreateDashboardInput, FilterInput
from src.modules.dashboards.application.use_cases import (
    AddWidgetUseCase,
    CreateDashboardUseCase,
    DeleteDashboardUseCase,
    GetDashboardUseCase,
    GetWidgetDataUseCase,
    ListDashboardsUseCase,
)
from src.modules.dashboards.presentation.dependencies import (
    get_add_widget_use_case,
    get_create_dashboard_use_case,
    get_delete_dashboard_use_case,
    get_get_dashboard_use_case,
    get_list_dashboards_use_case,
    get_widget_data_use_case,
)
from src.modules.dashboards.presentation.schemas import (
    AddWidgetRequest,
    CreateDashboardRequest,
    DashboardResponse,
    WidgetDataResponse,
    WidgetResponse,
)

router = APIRouter(prefix="/dashboards", tags=["dashboards"])


@router.post(
    "",
    response_model=DashboardResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new (empty) dashboard",
)
async def create_dashboard(
    body: CreateDashboardRequest,
    user: User = Depends(RequirePermission(Permission.DASHBOARD_CREATE)),
    use_case: CreateDashboardUseCase = Depends(get_create_dashboard_use_case),
) -> DashboardResponse:
    output = await use_case.execute(
        CreateDashboardInput(
            organization_id=user.organization_id,
            owner_user_id=str(user.id),
            name=body.name,
            description=body.description,
            is_public=body.is_public,
        )
    )
    return DashboardResponse(**_dashboard_dict(output))


@router.post(
    "/{dashboard_id}/widgets",
    response_model=DashboardResponse,
    summary="Add a widget (chart) to a dashboard",
    description=(
        "The widget's `table`/`dimension`/`measure`/`aggregation`/`filters` "
        "form a declarative aggregation spec — never raw SQL — which is "
        "compiled server-side into a parameterized query against the "
        "widget's data source at render time."
    ),
)
async def add_widget(
    dashboard_id: uuid.UUID,
    body: AddWidgetRequest,
    user: User = Depends(RequirePermission(Permission.DASHBOARD_EDIT)),
    use_case: AddWidgetUseCase = Depends(get_add_widget_use_case),
) -> DashboardResponse:
    output = await use_case.execute(
        AddWidgetInput(
            dashboard_id=str(dashboard_id),
            title=body.title,
            chart_type=body.chart_type,
            datasource_id=body.datasource_id,
            table=body.table,
            dimension=body.dimension,
            measure=body.measure,
            aggregation=body.aggregation,
            filters=[FilterInput(field=f.field, operator=f.operator, value=f.value) for f in body.filters],
            limit=body.limit,
            position=body.position,
        )
    )
    return DashboardResponse(**_dashboard_dict(output))


@router.get(
    "/{dashboard_id}",
    response_model=DashboardResponse,
    summary="Get a dashboard and its widget definitions",
)
async def get_dashboard(
    dashboard_id: uuid.UUID,
    user: User = Depends(RequirePermission(Permission.DASHBOARD_VIEW)),
    use_case: GetDashboardUseCase = Depends(get_get_dashboard_use_case),
) -> DashboardResponse:
    output = await use_case.execute(dashboard_id)
    return DashboardResponse(**_dashboard_dict(output))


@router.get(
    "",
    response_model=list[DashboardResponse],
    summary="List dashboards visible to the current organization",
)
async def list_dashboards(
    user: User = Depends(RequirePermission(Permission.DASHBOARD_VIEW)),
    use_case: ListDashboardsUseCase = Depends(get_list_dashboards_use_case),
) -> list[DashboardResponse]:
    items = await use_case.execute(user.organization_id)
    return [DashboardResponse(**_dashboard_dict(i)) for i in items]


@router.delete(
    "/{dashboard_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a dashboard",
)
async def delete_dashboard(
    dashboard_id: uuid.UUID,
    user: User = Depends(RequirePermission(Permission.DASHBOARD_DELETE)),
    use_case: DeleteDashboardUseCase = Depends(get_delete_dashboard_use_case),
) -> None:
    await use_case.execute(dashboard_id)


@router.get(
    "/{dashboard_id}/widgets/{widget_id}/data",
    response_model=WidgetDataResponse,
    summary="Execute (or serve cached) data for one widget",
    description=(
        "Runs the widget's compiled query against its data source, caching "
        "the result in Redis for `QUERY_CACHE_TTL_SECONDS` keyed on the "
        "full query fingerprint. `cache_status` in the response tells the "
        "client whether this was a hit or a fresh execution."
    ),
)
async def get_widget_data(
    dashboard_id: uuid.UUID,
    widget_id: uuid.UUID,
    user: User = Depends(RequirePermission(Permission.DASHBOARD_VIEW)),
    use_case: GetWidgetDataUseCase = Depends(get_widget_data_use_case),
) -> WidgetDataResponse:
    output = await use_case.execute(dashboard_id, widget_id)
    return WidgetDataResponse(
        columns=output.columns,
        rows=[list(r) for r in output.rows],
        truncated=output.truncated,
        cache_status=output.cache_status,
    )


def _dashboard_dict(output) -> dict:  # type: ignore[no-untyped-def]
    return {
        "id": output.id,
        "name": output.name,
        "description": output.description,
        "is_public": output.is_public,
        "widgets": [WidgetResponse(**w.__dict__) for w in output.widgets],
    }
