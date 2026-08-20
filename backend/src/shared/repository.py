"""Generic repository + Unit-of-Work protocols.

These are `typing.Protocol`s, not base classes: each module's
`domain/repositories.py` declares a narrow, entity-specific interface (e.g.
`UserRepository`) that structurally satisfies `Repository[User]`. The
application layer's use cases type-hint against the domain protocol; the
infrastructure layer provides a SQLAlchemy implementation. Swapping
persistence (or faking it in tests) never touches application code.
"""
from __future__ import annotations

import uuid
from typing import Protocol, TypeVar

T = TypeVar("T")


class Repository(Protocol[T]):
    async def get_by_id(self, entity_id: uuid.UUID) -> T | None: ...

    async def add(self, entity: T) -> None: ...

    async def delete(self, entity: T) -> None: ...


class UnitOfWorkProtocol(Protocol):
    async def commit(self) -> None: ...

    async def rollback(self) -> None: ...

    async def __aenter__(self) -> "UnitOfWorkProtocol": ...

    async def __aexit__(self, exc_type: object, exc: object, tb: object) -> None: ...
