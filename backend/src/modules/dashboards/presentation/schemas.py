from __future__ import annotations

from pydantic import BaseModel, Field


class FilterSchema(BaseModel):
    field: str
    operator: str
    value: object


class CreateDashboardRequest(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    description: str = ""
    is_public: bool = False


class AddWidgetRequest(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    chart_type: str = Field(description="line | bar | donut | kpi | table")
    datasource_id: str
    table: str
    dimension: str | None = None
    measure: str
    aggregation: str = Field(description="sum | avg | count | min | max")
    filters: list[FilterSchema] = Field(default_factory=list)
    limit: int = 1000
    position: dict[str, int] | None = None


class WidgetResponse(BaseModel):
    id: str
    title: str
    chart_type: str
    datasource_id: str
    position: dict[str, int]


class DashboardResponse(BaseModel):
    id: str
    name: str
    description: str
    is_public: bool
    widgets: list[WidgetResponse]


class WidgetDataResponse(BaseModel):
    columns: list[str]
    rows: list[list[object]]
    truncated: bool
    cache_status: str
