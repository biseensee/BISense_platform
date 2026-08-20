from src.core.exceptions import DataSourceConnectionError, EntityNotFoundError


class DataSourceNotFoundError(EntityNotFoundError):
    def __init__(self, datasource_id: object) -> None:
        super().__init__("DataSource", datasource_id)


class UnsupportedDataSourceTypeError(DataSourceConnectionError):
    def __init__(self, type_name: str) -> None:
        super().__init__(f"No connector registered for datasource type {type_name!r}")


class ConnectionTestFailedError(DataSourceConnectionError):
    def __init__(self, reason: str) -> None:
        super().__init__(f"Connection test failed: {reason}")
