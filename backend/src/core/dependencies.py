"""Shared FastAPI dependency providers.

Every module's `presentation/dependencies.py` builds its use-case wiring on
top of `get_db_session` / `get_cache` / `get_jwt_service` — this is the only
place that reaches into `request.app.state`, so modules stay decoupled from
how the composition root (`main.py`) constructed those singletons.
"""
from __future__ import annotations

from collections.abc import AsyncIterator

from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from src.config import Settings, get_settings
from src.core.cache import CachePort
from src.core.database import UnitOfWork
from src.core.security import JWTService


async def get_db_session(request: Request) -> AsyncIterator[AsyncSession]:
    database = request.app.state.database
    async with database.session() as session:
        yield session


async def get_uow(session: AsyncSession = Depends(get_db_session)) -> UnitOfWork:
    return UnitOfWork(session)


def get_cache(request: Request) -> CachePort:
    return request.app.state.cache


def get_jwt_service(settings: Settings = Depends(get_settings)) -> JWTService:
    return JWTService(settings)
