"""Auth domain: User, Role, Permission — pure business objects.

No SQLAlchemy, no Pydantic, no FastAPI imports here. Business rules (e.g.
"a user must have at least one role", "cannot deactivate the last admin")
belong on these entities or in application-layer use cases, never in the
ORM model or the API schema.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum

from src.shared.domain import AggregateRoot


class SystemRole(StrEnum):
    """Built-in roles seeded by the initial migration. Organizations may
    define additional custom roles composed of the same Permission set.
    """

    ADMIN = "admin"
    EDITOR = "editor"
    VIEWER = "viewer"


class Permission(StrEnum):
    DASHBOARD_CREATE = "dashboard:create"
    DASHBOARD_EDIT = "dashboard:edit"
    DASHBOARD_DELETE = "dashboard:delete"
    DASHBOARD_VIEW = "dashboard:view"
    DASHBOARD_SHARE = "dashboard:share"
    DATASOURCE_CREATE = "datasource:create"
    DATASOURCE_EDIT = "datasource:edit"
    DATASOURCE_DELETE = "datasource:delete"
    DATASOURCE_VIEW = "datasource:view"
    USER_MANAGE = "user:manage"


ROLE_PERMISSIONS: dict[SystemRole, frozenset[Permission]] = {
    SystemRole.ADMIN: frozenset(Permission),
    SystemRole.EDITOR: frozenset(
        {
            Permission.DASHBOARD_CREATE,
            Permission.DASHBOARD_EDIT,
            Permission.DASHBOARD_VIEW,
            Permission.DASHBOARD_SHARE,
            Permission.DATASOURCE_VIEW,
        }
    ),
    SystemRole.VIEWER: frozenset({Permission.DASHBOARD_VIEW, Permission.DATASOURCE_VIEW}),
}


@dataclass(kw_only=True)
class Role:
    name: SystemRole
    permissions: frozenset[Permission] = field(default_factory=frozenset)

    @classmethod
    def system(cls, role: SystemRole) -> "Role":
        return cls(name=role, permissions=ROLE_PERMISSIONS[role])


@dataclass(kw_only=True)
class User(AggregateRoot):
    email: str
    hashed_password: str
    full_name: str
    organization_id: str
    roles: list[SystemRole] = field(default_factory=lambda: [SystemRole.VIEWER])
    is_active: bool = True

    @property
    def permissions(self) -> frozenset[Permission]:
        result: set[Permission] = set()
        for role in self.roles:
            result |= ROLE_PERMISSIONS[role]
        return frozenset(result)

    def has_permission(self, permission: Permission) -> bool:
        return permission in self.permissions

    def deactivate(self) -> None:
        self.is_active = False
        self.touch()

    def assign_role(self, role: SystemRole) -> None:
        if role not in self.roles:
            self.roles.append(role)
            self.touch()
