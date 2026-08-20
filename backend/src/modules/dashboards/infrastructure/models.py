from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import JSON, Boolean, DateTime, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.database import Base


class DashboardModel(Base):
    __tablename__ = "dashboards"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    organization_id: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(String(2000), default="", nullable=False)
    owner_user_id: Mapped[str] = mapped_column(String(64), nullable=False)
    is_public: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    widgets: Mapped[list["WidgetModel"]] = relationship(
        back_populates="dashboard", cascade="all, delete-orphan", lazy="selectin"
    )


class WidgetModel(Base):
    __tablename__ = "widgets"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    dashboard_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("dashboards.id", ondelete="CASCADE"), index=True
    )
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    chart_type: Mapped[str] = mapped_column(String(16), nullable=False)
    datasource_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    # AggregationSpec serialized as JSON — table/dimension/measure/aggregation/filters/limit
    spec: Mapped[dict] = mapped_column(JSON, nullable=False)
    position_x: Mapped[int] = mapped_column(Integer, default=0)
    position_y: Mapped[int] = mapped_column(Integer, default=0)
    position_w: Mapped[int] = mapped_column(Integer, default=4)
    position_h: Mapped[int] = mapped_column(Integer, default=3)

    dashboard: Mapped[DashboardModel] = relationship(back_populates="widgets")
