"""Maps `DataSourceType` -> `Connector` implementation.

Adding a warehouse type: implement `Connector` in a new module, register it
here. Nothing else in the codebase branches on datasource type by name.
"""
from __future__ import annotations

from src.modules.datasources.domain.entities import DataSourceType
from src.modules.datasources.domain.exceptions import UnsupportedDataSourceTypeError
from src.modules.datasources.infrastructure.connectors.base import Connector
from src.modules.datasources.infrastructure.connectors.clickhouse import ClickHouseConnector
from src.modules.datasources.infrastructure.connectors.postgres import PostgresConnector

_REGISTRY: dict[DataSourceType, Connector] = {
    DataSourceType.POSTGRESQL: PostgresConnector(),
    DataSourceType.CLICKHOUSE: ClickHouseConnector(),
    # DataSourceType.MYSQL / CSV_UPLOAD: add connectors here following the
    # same Protocol; omitted from this skeleton for brevity.
}


class ConnectorRegistry:
    @staticmethod
    def get(datasource_type: DataSourceType) -> Connector:
        connector = _REGISTRY.get(datasource_type)
        if connector is None:
            raise UnsupportedDataSourceTypeError(datasource_type.value)
        return connector
