"""Dashboards domain: Dashboard (aggregate root) owns a list of Widgets.

A Widget references a DataSource by id (cross-module reference by id only —
`dashboards` never imports `datasources.domain` types, keeping module
boundaries enforceable) and carries a declarative `AggregationSpec` that the
application layer compiles into a `QuerySpec` for the chosen connector.
"""
from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from enum import StrEnum

from src.shared.domain import AggregateRoot, Entity


class ChartType(StrEnum):
    LINE = "line"
    BAR = "bar"
    DONUT = "donut"
    KPI = "kpi"
    TABLE = "table"


class AggregationFunction(StrEnum):
    SUM = "sum"
    AVG = "avg"
    COUNT = "count"
    MIN = "min"
    MAX = "max"


@dataclass(kw_only=True)
class Filter:
    field: str
    operator: str  # "=", "!=", ">", "<", "in", "between"
    value: object


@dataclass(kw_only=True)
class AggregationSpec:
    """Declarative shape of a widget's query — never raw SQL from the
    client. The application layer's query compiler turns this into a
    parameterized `QuerySpec` for the target connector.
    """

    table: str
    dimension: str | None
    measure: str
    aggregation: AggregationFunction
    filters: list[Filter] = field(default_factory=list)
    limit: int = 1000


@dataclass(kw_only=True)
class Widget(Entity):
    dashboard_id: uuid.UUID
    title: str
    chart_type: ChartType
    datasource_id: uuid.UUID
    spec: AggregationSpec
    position: dict[str, int] = field(default_factory=lambda: {"x": 0, "y": 0, "w": 4, "h": 3})


@dataclass(kw_only=True)
class Dashboard(AggregateRoot):
    organization_id: str
    name: str
    description: str = ""
    owner_user_id: str = ""
    is_public: bool = False
    widgets: list[Widget] = field(default_factory=list)

    def add_widget(self, widget: Widget) -> None:
        widget.dashboard_id = self.id
        self.widgets.append(widget)
        self.touch()

    def remove_widget(self, widget_id: uuid.UUID) -> None:
        self.widgets = [w for w in self.widgets if w.id != widget_id]
        self.touch()
