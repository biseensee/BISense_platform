"""Base building blocks for the domain layer, shared across all modules.

Every module's `domain/entities.py` builds on these — never on SQLAlchemy or
Pydantic. Domain entities are plain Python; ORM mapping lives entirely in
each module's `infrastructure/models.py`, and API schemas in
`presentation/schemas.py`. This keeps business rules testable without a
database or an HTTP framework.
"""
from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime


def new_id() -> uuid.UUID:
    return uuid.uuid4()


def utcnow() -> datetime:
    return datetime.now(UTC)


@dataclass(kw_only=True)
class Entity:
    """An object defined by identity, not attributes."""

    id: uuid.UUID = field(default_factory=new_id)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Entity):
            return NotImplemented
        return type(self) is type(other) and self.id == other.id

    def __hash__(self) -> int:
        return hash((type(self), self.id))


@dataclass(kw_only=True)
class AggregateRoot(Entity):
    """An Entity that is the consistency boundary for a cluster of objects
    and the transaction/repository boundary (e.g. Dashboard owns Widgets).

    Domain events are collected here and drained by the application layer
    after a successful commit (outbox pattern hook point) rather than
    dispatched inline, so persistence failures never leave a "half fired"
    side effect.
    """

    created_at: datetime = field(default_factory=utcnow)
    updated_at: datetime = field(default_factory=utcnow)
    _domain_events: list[object] = field(default_factory=list, repr=False, compare=False)

    def record_event(self, event: object) -> None:
        self._domain_events.append(event)

    def pull_events(self) -> list[object]:
        events, self._domain_events = self._domain_events, []
        return events

    def touch(self) -> None:
        self.updated_at = utcnow()
