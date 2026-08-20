"""SQLAlchemy implementation of `UserRepository`."""
from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.auth.domain.entities import SystemRole, User
from src.modules.auth.infrastructure.models import UserModel


def _to_domain(row: UserModel) -> User:
    return User(
        id=row.id,
        email=row.email,
        hashed_password=row.hashed_password,
        full_name=row.full_name,
        organization_id=row.organization_id,
        roles=[SystemRole(r) for r in row.roles],
        is_active=row.is_active,
        created_at=row.created_at,
        updated_at=row.updated_at,
    )


def _to_row(user: User) -> UserModel:
    return UserModel(
        id=user.id,
        organization_id=user.organization_id,
        email=user.email,
        hashed_password=user.hashed_password,
        full_name=user.full_name,
        roles=[r.value for r in user.roles],
        is_active=user.is_active,
        created_at=user.created_at,
        updated_at=user.updated_at,
    )


class SqlAlchemyUserRepository:
    """Implements `auth.domain.repositories.UserRepository`."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, user_id: uuid.UUID) -> User | None:
        row = await self._session.get(UserModel, user_id)
        return _to_domain(row) if row else None

    async def get_by_email(self, email: str, *, organization_id: str) -> User | None:
        stmt = select(UserModel).where(
            UserModel.email == email, UserModel.organization_id == organization_id
        )
        row = (await self._session.execute(stmt)).scalar_one_or_none()
        return _to_domain(row) if row else None

    async def add(self, user: User) -> None:
        self._session.add(_to_row(user))
        await self._session.flush()

    async def update(self, user: User) -> None:
        row = await self._session.get(UserModel, user.id)
        if row is None:
            return
        row.full_name = user.full_name
        row.roles = [r.value for r in user.roles]
        row.is_active = user.is_active
        row.updated_at = user.updated_at
        await self._session.flush()

    async def list_by_organization(self, organization_id: str) -> list[User]:
        stmt = select(UserModel).where(UserModel.organization_id == organization_id)
        rows = (await self._session.execute(stmt)).scalars().all()
        return [_to_domain(r) for r in rows]
