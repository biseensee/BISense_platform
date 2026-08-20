from __future__ import annotations

import uuid
from typing import Protocol

from src.modules.dashboards.domain.entities import Dashboard


class DashboardRepository(Protocol):
    async def get_by_id(self, dashboard_id: uuid.UUID) -> Dashboard | None: ...

    async def add(self, dashboard: Dashboard) -> None: ...

    async def update(self, dashboard: Dashboard) -> None: ...

    async def delete(self, dashboard: Dashboard) -> None: ...

    async def list_by_organization(self, organization_id: str) -> list[Dashboard]: ...
