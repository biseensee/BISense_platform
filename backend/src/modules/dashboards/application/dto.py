from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True, slots=True)
class FilterInput:
    field: str
    operator: str
    value: object


@dataclass(frozen=True, slots=True)
class CreateDashboardInput:
    organization_id: str
    owner_user_id: str
    name: str
    description: str = ""
    is_public: bool = False


@dataclass(frozen=True, slots=True)
class AddWidgetInput:
    dashboard_id: str
    title: str
    chart_type: str
    datasource_id: str
    table: str
    dimension: str | None
    measure: str
    aggregation: str
    filters: list[FilterInput] = field(default_factory=list)
    limit: int = 1000
    position: dict[str, int] | None = None


@dataclass(frozen=True, slots=True)
class WidgetOutput:
    id: str
    title: str
    chart_type: str
    datasource_id: str
    position: dict[str, int]


@dataclass(frozen=True, slots=True)
class DashboardOutput:
    id: str
    name: str
    description: str
    is_public: bool
    widgets: list[WidgetOutput]


@dataclass(frozen=True, slots=True)
class WidgetDataOutput:
    columns: list[str]
    rows: list[tuple]
    truncated: bool
    cache_status: str  # "hit" | "miss"
