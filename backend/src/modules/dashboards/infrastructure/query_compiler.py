"""Compiles a widget's declarative `AggregationSpec` into a connector
`QuerySpec`.

Identifiers (table/column names) can't be bound as query parameters in SQL,
so they're validated against a strict allow-list pattern and double-quoted
instead — this is what actually prevents injection, not string escaping.
Values (filter operands) are always passed as bound parameters, never
interpolated into the SQL string.
"""
from __future__ import annotations

import re

from src.core.exceptions import ValidationError
from src.modules.dashboards.domain.entities import AggregationSpec
from src.modules.datasources.infrastructure.connectors.base import QuerySpec

_IDENTIFIER_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]{0,127}$")

_OPERATOR_SQL = {
    "=": "=",
    "!=": "!=",
    ">": ">",
    "<": "<",
    ">=": ">=",
    "<=": "<=",
    "in": "= ANY",
}


def _quote_identifier(name: str) -> str:
    if not _IDENTIFIER_RE.match(name):
        raise ValidationError(f"Invalid identifier: {name!r}")
    return f'"{name}"'


def compile_widget_query(spec: AggregationSpec) -> QuerySpec:
    table = _quote_identifier(spec.table)
    measure = _quote_identifier(spec.measure)
    agg = spec.aggregation.value.upper()

    select_parts = [f"{agg}({measure}) AS value"]
    group_by = ""
    if spec.dimension:
        dimension = _quote_identifier(spec.dimension)
        select_parts.insert(0, f"{dimension} AS dimension")
        group_by = f" GROUP BY {dimension}"

    where_clauses: list[str] = []
    params: dict[str, object] = {}
    for i, f in enumerate(spec.filters):
        field = _quote_identifier(f.field)
        if f.operator not in _OPERATOR_SQL:
            raise ValidationError(f"Unsupported filter operator: {f.operator!r}")
        param_name = f"p{i}"
        where_clauses.append(f"{field} {_OPERATOR_SQL[f.operator]} :{param_name}")
        params[param_name] = f.value

    where_sql = f" WHERE {' AND '.join(where_clauses)}" if where_clauses else ""
    sql = f"SELECT {', '.join(select_parts)} FROM {table}{where_sql}{group_by}"

    return QuerySpec(sql=sql, params=params, row_limit=spec.limit)
