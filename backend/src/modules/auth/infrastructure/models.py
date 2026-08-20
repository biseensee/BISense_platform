"""SQLAlchemy ORM models for the auth module.

Mapping between ORM rows and domain entities happens in `repositories.py`
(`_to_domain` / `_to_row`) — the domain `User` dataclass never inherits from
`Base`, so domain unit tests don't need a database at all.
"""
from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import ARRAY, Boolean, DateTime, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from src.core.database import Base


class UserModel(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    organization_id: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    email: Mapped[str] = mapped_column(String(320), nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(String(200), nullable=False)
    roles: Mapped[list[str]] = mapped_column(ARRAY(String(32)), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    __table_args__ = (
        # One email per organization — multi-tenant uniqueness, not global.
        {"schema": None},
    )
