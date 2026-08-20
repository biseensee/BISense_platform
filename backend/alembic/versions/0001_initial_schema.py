"""initial schema: users, data_sources, dashboards, widgets, audit_log

Revision ID: 0001_initial_schema
Revises:
Create Date: 2026-08-20
"""
from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0001_initial_schema"
down_revision: str | None = None
branch_labels: Sequence[str] | str | None = None
depends_on: Sequence[str] | str | None = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("organization_id", sa.String(64), nullable=False),
        sa.Column("email", sa.String(320), nullable=False),
        sa.Column("hashed_password", sa.String(255), nullable=False),
        sa.Column("full_name", sa.String(200), nullable=False),
        sa.Column("roles", postgresql.ARRAY(sa.String(32)), nullable=False),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_users_organization_id", "users", ["organization_id"])
    # Unique per-tenant, not global — two orgs may have users with the same email.
    op.create_unique_constraint(
        "uq_users_org_email", "users", ["organization_id", "email"]
    )

    op.create_table(
        "data_sources",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("organization_id", sa.String(64), nullable=False),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("type", sa.String(32), nullable=False),
        sa.Column("host", sa.String(255), nullable=False),
        sa.Column("port", sa.Integer, nullable=False),
        sa.Column("database_name", sa.String(200), nullable=False),
        sa.Column("username", sa.String(200), nullable=False),
        sa.Column("extra", sa.JSON, nullable=False, server_default="{}"),
        sa.Column("encrypted_credentials", sa.LargeBinary, nullable=False),
        sa.Column("status", sa.String(16), nullable=False, server_default="pending"),
        sa.Column("last_connection_error", sa.String(1000), nullable=True),
        sa.Column("created_by_user_id", sa.String(64), nullable=False, server_default=""),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_data_sources_organization_id", "data_sources", ["organization_id"])

    op.create_table(
        "dashboards",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("organization_id", sa.String(64), nullable=False),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("description", sa.String(2000), nullable=False, server_default=""),
        sa.Column("owner_user_id", sa.String(64), nullable=False),
        sa.Column("is_public", sa.Boolean, nullable=False, server_default=sa.false()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_dashboards_organization_id", "dashboards", ["organization_id"])

    op.create_table(
        "widgets",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "dashboard_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("dashboards.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("title", sa.String(200), nullable=False),
        sa.Column("chart_type", sa.String(16), nullable=False),
        sa.Column("datasource_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("spec", sa.JSON, nullable=False),
        sa.Column("position_x", sa.Integer, nullable=False, server_default="0"),
        sa.Column("position_y", sa.Integer, nullable=False, server_default="0"),
        sa.Column("position_w", sa.Integer, nullable=False, server_default="4"),
        sa.Column("position_h", sa.Integer, nullable=False, server_default="3"),
    )
    op.create_index("ix_widgets_dashboard_id", "widgets", ["dashboard_id"])

    # Append-only audit trail for privileged actions (login, datasource
    # create/delete, dashboard share). Written by an application-layer
    # decorator/event hook, not modeled as a dataclass module of its own in
    # this skeleton — flagged as the natural next module to add.
    op.create_table(
        "audit_log",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("organization_id", sa.String(64), nullable=False),
        sa.Column("actor_user_id", sa.String(64), nullable=False),
        sa.Column("action", sa.String(100), nullable=False),
        sa.Column("resource_type", sa.String(50), nullable=False),
        sa.Column("resource_id", sa.String(64), nullable=True),
        sa.Column("metadata", sa.JSON, nullable=False, server_default="{}"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_audit_log_organization_id", "audit_log", ["organization_id"])
    op.create_index("ix_audit_log_created_at", "audit_log", ["created_at"])


def downgrade() -> None:
    op.drop_table("audit_log")
    op.drop_index("ix_widgets_dashboard_id", table_name="widgets")
    op.drop_table("widgets")
    op.drop_index("ix_dashboards_organization_id", table_name="dashboards")
    op.drop_table("dashboards")
    op.drop_index("ix_data_sources_organization_id", table_name="data_sources")
    op.drop_table("data_sources")
    op.drop_constraint("uq_users_org_email", "users", type_="unique")
    op.drop_index("ix_users_organization_id", table_name="users")
    op.drop_table("users")
