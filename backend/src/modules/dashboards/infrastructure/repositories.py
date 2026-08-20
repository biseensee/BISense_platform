from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.dashboards.domain.entities import (
    AggregationFunction,
    AggregationSpec,
    ChartType,
    Dashboard,
    Filter,
    Widget,
)
from src.modules.dashboards.infrastructure.models import DashboardModel, WidgetModel


def _widget_to_domain(row: WidgetModel) -> Widget:
    spec = row.spec
    return Widget(
        id=row.id,
        dashboard_id=row.dashboard_id,
        title=row.title,
        chart_type=ChartType(row.chart_type),
        datasource_id=row.datasource_id,
        spec=AggregationSpec(
            table=spec["table"],
            dimension=spec.get("dimension"),
            measure=spec["measure"],
            aggregation=AggregationFunction(spec["aggregation"]),
            filters=[Filter(**f) for f in spec.get("filters", [])],
            limit=spec.get("limit", 1000),
        ),
        position={
            "x": row.position_x,
            "y": row.position_y,
            "w": row.position_w,
            "h": row.position_h,
        },
    )


def _widget_to_row(widget: Widget) -> WidgetModel:
    return WidgetModel(
        id=widget.id,
        dashboard_id=widget.dashboard_id,
        title=widget.title,
        chart_type=widget.chart_type.value,
        datasource_id=widget.datasource_id,
        spec={
            "table": widget.spec.table,
            "dimension": widget.spec.dimension,
            "measure": widget.spec.measure,
            "aggregation": widget.spec.aggregation.value,
            "filters": [
                {"field": f.field, "operator": f.operator, "value": f.value}
                for f in widget.spec.filters
            ],
            "limit": widget.spec.limit,
        },
        position_x=widget.position.get("x", 0),
        position_y=widget.position.get("y", 0),
        position_w=widget.position.get("w", 4),
        position_h=widget.position.get("h", 3),
    )


def _dashboard_to_domain(row: DashboardModel) -> Dashboard:
    return Dashboard(
        id=row.id,
        organization_id=row.organization_id,
        name=row.name,
        description=row.description,
        owner_user_id=row.owner_user_id,
        is_public=row.is_public,
        widgets=[_widget_to_domain(w) for w in row.widgets],
        created_at=row.created_at,
        updated_at=row.updated_at,
    )


class SqlAlchemyDashboardRepository:
    """Implements `dashboards.domain.repositories.DashboardRepository`.

    Widgets are persisted as a whole with the dashboard (simple
    replace-all-on-save strategy) — adequate at this dashboard/widget
    cardinality; a granular widget-level repository is a straightforward
    extension if partial updates become a bottleneck.
    """

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, dashboard_id: uuid.UUID) -> Dashboard | None:
        row = await self._session.get(DashboardModel, dashboard_id)
        return _dashboard_to_domain(row) if row else None

    async def add(self, dashboard: Dashboard) -> None:
        row = DashboardModel(
            id=dashboard.id,
            organization_id=dashboard.organization_id,
            name=dashboard.name,
            description=dashboard.description,
            owner_user_id=dashboard.owner_user_id,
            is_public=dashboard.is_public,
            created_at=dashboard.created_at,
            updated_at=dashboard.updated_at,
            widgets=[_widget_to_row(w) for w in dashboard.widgets],
        )
        self._session.add(row)
        await self._session.flush()

    async def update(self, dashboard: Dashboard) -> None:
        row = await self._session.get(DashboardModel, dashboard.id)
        if row is None:
            return
        row.name = dashboard.name
        row.description = dashboard.description
        row.is_public = dashboard.is_public
        row.updated_at = dashboard.updated_at
        row.widgets = [_widget_to_row(w) for w in dashboard.widgets]
        await self._session.flush()

    async def delete(self, dashboard: Dashboard) -> None:
        row = await self._session.get(DashboardModel, dashboard.id)
        if row is not None:
            await self._session.delete(row)
            await self._session.flush()

    async def list_by_organization(self, organization_id: str) -> list[Dashboard]:
        stmt = select(DashboardModel).where(
            DashboardModel.organization_id == organization_id
        )
        rows = (await self._session.execute(stmt)).scalars().all()
        return [_dashboard_to_domain(r) for r in rows]
