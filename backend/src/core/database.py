"""Async SQLAlchemy engine/session management + Unit of Work.

Scaling notes (10+ TB / 1000+ concurrent users):
- The engine pool (`pool_size` + `max_overflow`) bounds connections held by
  *this* process; in production, point `DATABASE_HOST` at a PgBouncer
  (transaction pooling) endpoint so many API pods can share a much smaller
  number of real Postgres backend connections.
- Read-heavy dashboard queries should go through `get_read_session`, which
  can be pointed at a read-replica DSN via `POSTGRES_REPLICA_HOST` in a
  later iteration without touching call sites.
- Large analytical scans (the actual dashboard *data*, as opposed to
  platform metadata) are never run against this Postgres — they go through
  the `datasources` module's connectors (Postgres/ClickHouse/etc.) against
  the customer's own warehouse. This database only stores platform metadata
  (users, dashboards, datasource configs, audit log), which stays small and
  fits comfortably behind normal OLTP scaling.
"""
from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Self

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from src.config import Settings


class Base(DeclarativeBase):
    """Shared declarative base for all SQLAlchemy ORM models."""


class Database:
    """Owns the engine + sessionmaker lifecycle for the app process."""

    def __init__(self, settings: Settings) -> None:
        self.engine: AsyncEngine = create_async_engine(
            settings.database_url,
            pool_size=settings.database_pool_size,
            max_overflow=settings.database_max_overflow,
            pool_timeout=settings.database_pool_timeout,
            pool_pre_ping=True,
            echo=settings.debug,
        )
        self.session_factory = async_sessionmaker(
            bind=self.engine, expire_on_commit=False, autoflush=False
        )

    async def dispose(self) -> None:
        await self.engine.dispose()

    @asynccontextmanager
    async def session(self) -> AsyncIterator[AsyncSession]:
        async with self.session_factory() as session:
            yield session


class UnitOfWork:
    """Transaction boundary spanning one or more repositories.

    Use cases depend on this (or a narrower protocol) rather than on
    SQLAlchemy directly, so the application layer stays persistence-agnostic
    and can be unit-tested with an in-memory fake.
    """

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(self, exc_type: object, exc: object, tb: object) -> None:
        if exc_type is not None:
            await self.session.rollback()
        # commit is explicit via `commit()` — callers opt in rather than the
        # UoW guessing intent on clean exit.

    async def commit(self) -> None:
        await self.session.commit()

    async def rollback(self) -> None:
        await self.session.rollback()
