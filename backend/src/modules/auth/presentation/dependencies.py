"""Auth wiring: repository/use-case factories, `get_current_user`, and the
RBAC dependency other modules import to guard their own endpoints.
"""
from __future__ import annotations

import uuid

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.dependencies import get_db_session, get_jwt_service, get_uow
from src.core.security import JWTService, TokenType
from src.modules.auth.application.use_cases import (
    AuthenticateUserUseCase,
    RefreshTokenUseCase,
    RegisterUserUseCase,
)
from src.modules.auth.domain.entities import Permission, User
from src.modules.auth.domain.exceptions import InactiveUserError, InvalidTokenError
from src.modules.auth.infrastructure.repositories import SqlAlchemyUserRepository

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login", auto_error=False)


def get_user_repository(session: AsyncSession = Depends(get_db_session)) -> SqlAlchemyUserRepository:
    return SqlAlchemyUserRepository(session)


def get_register_use_case(
    users: SqlAlchemyUserRepository = Depends(get_user_repository),
    uow=Depends(get_uow),
) -> RegisterUserUseCase:
    return RegisterUserUseCase(users, uow)


def get_authenticate_use_case(
    users: SqlAlchemyUserRepository = Depends(get_user_repository),
    jwt_service: JWTService = Depends(get_jwt_service),
) -> AuthenticateUserUseCase:
    return AuthenticateUserUseCase(users, jwt_service)


def get_refresh_use_case(
    users: SqlAlchemyUserRepository = Depends(get_user_repository),
    jwt_service: JWTService = Depends(get_jwt_service),
) -> RefreshTokenUseCase:
    return RefreshTokenUseCase(users, jwt_service)


async def get_current_user(
    token: str | None = Depends(oauth2_scheme),
    users: SqlAlchemyUserRepository = Depends(get_user_repository),
    jwt_service: JWTService = Depends(get_jwt_service),
) -> User:
    if token is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Not authenticated")
    try:
        payload = jwt_service.decode(token)
    except Exception as exc:  # jwt.InvalidTokenError and subclasses
        raise InvalidTokenError() from exc
    if payload.token_type is not TokenType.ACCESS:
        raise InvalidTokenError("Provided token is not an access token")

    user = await users.get_by_id(uuid.UUID(payload.subject))
    if user is None:
        raise InvalidTokenError("User no longer exists")
    if not user.is_active:
        raise InactiveUserError()
    return user


class RequirePermission:
    """RBAC guard: `Depends(RequirePermission(Permission.DASHBOARD_EDIT))`.

    A callable class (not a plain function) so it can be parameterized per
    route while still being a valid FastAPI dependency.
    """

    def __init__(self, permission: Permission) -> None:
        self._permission = permission

    def __call__(self, user: User = Depends(get_current_user)) -> User:
        if not user.has_permission(self._permission):
            raise HTTPException(
                status.HTTP_403_FORBIDDEN,
                f"Missing required permission: {self._permission.value}",
            )
        return user
