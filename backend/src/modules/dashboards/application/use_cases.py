"""Dashboard use cases, including the widget data-execution path:

    GetWidgetDataUseCase
        -> Redis cache lookup (core.cache)
        -> on miss: resolve DataSource -> pick Connector -> compile & run query
        -> cache the result, record Prometheus timing/hit-miss metrics

This is the module boundary where `dashboards` legitimately depends on
`datasources`' *public* interfaces (its repository protocol + infra
connector registry/cipher) — never on `datasources.presentation`.
"""
from __future__ import annotations

import time
import uuid

from src.core.cache import (
    CachePort,
    build_query_cache_key,
    record_cache_hit,
    record_cache_miss,
)
from src.core.metrics import DASHBOARD_QUERY_DURATION_SECONDS
from src.modules.dashboards.application.dto import (
    AddWidgetInput,
    CreateDashboardInput,
    DashboardOutput,
    WidgetDataOutput,
    WidgetOutput,
)
from src.modules.dashboards.domain.entities import (
    AggregationFunction,
    AggregationSpec,
    ChartType,
    Dashboard,
    Filter,
    Widget,
)
from src.modules.dashboards.domain.exceptions import DashboardNotFoundError, WidgetNotFoundError
from src.modules.dashboards.domain.repositories import DashboardRepository
from src.modules.dashboards.infrastructure.query_compiler import compile_widget_query
from src.modules.datasources.domain.exceptions import DataSourceNotFoundError
from src.modules.datasources.domain.repositories import DataSourceRepository
from src.modules.datasources.infrastructure.connectors.registry import ConnectorRegistry
from src.modules.datasources.infrastructure.crypto import CredentialCipher
from src.shared.repository import UnitOfWorkProtocol


def _widget_output(w: Widget) -> WidgetOutput:
    return WidgetOutput(
        id=str(w.id),
        title=w.title,
        chart_type=w.chart_type.value,
        datasource_id=str(w.datasource_id),
        position=w.position,
    )


def _dashboard_output(d: Dashboard) -> DashboardOutput:
    return DashboardOutput(
        id=str(d.id),
        name=d.name,
        description=d.description,
        is_public=d.is_public,
        widgets=[_widget_output(w) for w in d.widgets],
    )


class CreateDashboardUseCase:
    def __init__(self, repository: DashboardRepository, uow: UnitOfWorkProtocol) -> None:
        self._repository = repository
        self._uow = uow

    async def execute(self, data: CreateDashboardInput) -> DashboardOutput:
        dashboard = Dashboard(
            organization_id=data.organization_id,
            owner_user_id=data.owner_user_id,
            name=data.name,
            description=data.description,
            is_public=data.is_public,
        )
        async with self._uow:
            await self._repository.add(dashboard)
            await self._uow.commit()
        return _dashboard_output(dashboard)


class AddWidgetUseCase:
    def __init__(self, repository: DashboardRepository, uow: UnitOfWorkProtocol) -> None:
        self._repository = repository
        self._uow = uow

    async def execute(self, data: AddWidgetInput) -> DashboardOutput:
        dashboard = await self._repository.get_by_id(uuid.UUID(data.dashboard_id))
        if dashboard is None:
            raise DashboardNotFoundError(data.dashboard_id)

        widget = Widget(
            dashboard_id=dashboard.id,
            title=data.title,
            chart_type=ChartType(data.chart_type),
            datasource_id=uuid.UUID(data.datasource_id),
            spec=AggregationSpec(
                table=data.table,
                dimension=data.dimension,
                measure=data.measure,
                aggregation=AggregationFunction(data.aggregation),
                filters=[Filter(field=f.field, operator=f.operator, value=f.value) for f in data.filters],
                limit=data.limit,
            ),
            position=data.position or {"x": 0, "y": 0, "w": 4, "h": 3},
        )
        dashboard.add_widget(widget)

        async with self._uow:
            await self._repository.update(dashboard)
            await self._uow.commit()
        return _dashboard_output(dashboard)


class GetDashboardUseCase:
    def __init__(self, repository: DashboardRepository) -> None:
        self._repository = repository

    async def execute(self, dashboard_id: uuid.UUID) -> DashboardOutput:
        dashboard = await self._repository.get_by_id(dashboard_id)
        if dashboard is None:
            raise DashboardNotFoundError(dashboard_id)
        return _dashboard_output(dashboard)


class ListDashboardsUseCase:
    def __init__(self, repository: DashboardRepository) -> None:
        self._repository = repository

    async def execute(self, organization_id: str) -> list[DashboardOutput]:
        items = await self._repository.list_by_organization(organization_id)
        return [_dashboard_output(d) for d in items]


class DeleteDashboardUseCase:
    def __init__(self, repository: DashboardRepository, uow: UnitOfWorkProtocol) -> None:
        self._repository = repository
        self._uow = uow

    async def execute(self, dashboard_id: uuid.UUID) -> None:
        dashboard = await self._repository.get_by_id(dashboard_id)
        if dashboard is None:
            raise DashboardNotFoundError(dashboard_id)
        async with self._uow:
            await self._repository.delete(dashboard)
            await self._uow.commit()


class GetWidgetDataUseCase:
    """Executes (or serves from cache) the query backing one widget.

    Cache key incorporates the datasource id and the full query fingerprint
    (table/dimension/measure/aggregation/filters) — never just the widget
    id — so two tenants can't collide on a cache entry and a filter change
    always busts the cache correctly (see `core.cache.build_query_cache_key`).
    """

    def __init__(
        self,
        dashboard_repository: DashboardRepository,
        datasource_repository: DataSourceRepository,
        cipher: CredentialCipher,
        cache: CachePort,
        cache_ttl_seconds: int,
    ) -> None:
        self._dashboards = dashboard_repository
        self._datasources = datasource_repository
        self._cipher = cipher
        self._cache = cache
        self._ttl = cache_ttl_seconds

    async def execute(self, dashboard_id: uuid.UUID, widget_id: uuid.UUID) -> WidgetDataOutput:
        dashboard = await self._dashboards.get_by_id(dashboard_id)
        if dashboard is None:
            raise DashboardNotFoundError(dashboard_id)
        widget = next((w for w in dashboard.widgets if w.id == widget_id), None)
        if widget is None:
            raise WidgetNotFoundError(widget_id)

        datasource = await self._datasources.get_by_id(widget.datasource_id)
        if datasource is None:
            raise DataSourceNotFoundError(widget.datasource_id)

        fingerprint = {
            "table": widget.spec.table,
            "dimension": widget.spec.dimension,
            "measure": widget.spec.measure,
            "aggregation": widget.spec.aggregation.value,
            "filters": [(f.field, f.operator, f.value) for f in widget.spec.filters],
            "limit": widget.spec.limit,
        }
        cache_key = build_query_cache_key(
            module="dashboards", datasource_id=str(datasource.id), query_fingerprint=fingerprint
        )

        cached = await self._cache.get_json(cache_key)
        if cached is not None:
            record_cache_hit("dashboards")
            return WidgetDataOutput(
                columns=cached["columns"],
                rows=[tuple(r) for r in cached["rows"]],
                truncated=cached["truncated"],
                cache_status="hit",
            )
        record_cache_miss("dashboards")

        connector = ConnectorRegistry.get(datasource.type)
        credentials = self._cipher.decrypt(datasource.encrypted_credentials)
        query_spec = compile_widget_query(widget.spec)

        start = time.perf_counter()
        result = await connector.execute_query(datasource.config, credentials, query_spec)
        DASHBOARD_QUERY_DURATION_SECONDS.labels(
            datasource_type=datasource.type.value, cache_status="miss"
        ).observe(time.perf_counter() - start)

        await self._cache.set_json(
            cache_key,
            {"columns": result.columns, "rows": [list(r) for r in result.rows], "truncated": result.truncated},
            ttl_seconds=self._ttl,
        )
        return WidgetDataOutput(
            columns=result.columns, rows=result.rows, truncated=result.truncated, cache_status="miss"
        )
