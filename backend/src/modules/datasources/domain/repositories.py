from __future__ import annotations

import uuid
from typing import Protocol

from src.modules.datasources.domain.entities import DataSource


class DataSourceRepository(Protocol):
    async def get_by_id(self, datasource_id: uuid.UUID) -> DataSource | None: ...

    async def add(self, datasource: DataSource) -> None: ...

    async def update(self, datasource: DataSource) -> None: ...

    async def delete(self, datasource: DataSource) -> None: ...

    async def list_by_organization(self, organization_id: str) -> list[DataSource]: ...
