"""Repository interfaces for the auth module (Protocols, no implementation)."""
from __future__ import annotations

import uuid
from typing import Protocol

from src.modules.auth.domain.entities import User


class UserRepository(Protocol):
    async def get_by_id(self, user_id: uuid.UUID) -> User | None: ...

    async def get_by_email(self, email: str, *, organization_id: str) -> User | None: ...

    async def add(self, user: User) -> None: ...

    async def update(self, user: User) -> None: ...

    async def list_by_organization(self, organization_id: str) -> list[User]: ...
