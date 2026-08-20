"""Tests for the AggregationSpec -> QuerySpec compiler — the boundary that
keeps end-user-controlled dashboard filters from becoming SQL injection.
"""
from __future__ import annotations

import pytest

from src.core.exceptions import ValidationError
from src.modules.dashboards.domain.entities import AggregationFunction, AggregationSpec, Filter
from src.modules.dashboards.infrastructure.query_compiler import compile_widget_query


def test_compiles_simple_aggregation() -> None:
    spec = AggregationSpec(
        table="orders", dimension="region", measure="amount", aggregation=AggregationFunction.SUM
    )
    query = compile_widget_query(spec)

    assert '"region" AS dimension' in query.sql
    assert 'SUM("amount") AS value' in query.sql
    assert 'GROUP BY "region"' in query.sql
    assert query.params == {}


def test_filters_become_bound_parameters_not_string_concatenation() -> None:
    spec = AggregationSpec(
        table="orders",
        dimension=None,
        measure="amount",
        aggregation=AggregationFunction.SUM,
        filters=[Filter(field="status", operator="=", value="paid")],
    )
    query = compile_widget_query(spec)

    assert ":p0" in query.sql
    assert "paid" not in query.sql  # value never interpolated into SQL text
    assert query.params == {"p0": "paid"}


@pytest.mark.parametrize(
    "malicious_identifier",
    ['orders"; DROP TABLE users; --', "orders; SELECT * FROM secrets", "orders WHERE 1=1"],
)
def test_rejects_non_identifier_table_names(malicious_identifier: str) -> None:
    spec = AggregationSpec(
        table=malicious_identifier,
        dimension=None,
        measure="amount",
        aggregation=AggregationFunction.SUM,
    )
    with pytest.raises(ValidationError):
        compile_widget_query(spec)


def test_rejects_unsupported_operator() -> None:
    spec = AggregationSpec(
        table="orders",
        dimension=None,
        measure="amount",
        aggregation=AggregationFunction.SUM,
        filters=[Filter(field="status", operator="DROP", value="x")],
    )
    with pytest.raises(ValidationError):
        compile_widget_query(spec)
