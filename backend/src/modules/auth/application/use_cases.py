"""Auth use cases — one class per use case (command/query), the application
layer's entry points. Each depends only on domain interfaces + `core`
primitives (JWTService, UnitOfWork), never on FastAPI or SQLAlchemy models
directly — that keeps them trivially unit-testable with in-memory fakes.
"""
from __future__ import annotations

import uuid

from src.core.security import JWTService, TokenType, hash_password, verify_password
from src.modules.auth.application.dto import (
    AuthenticateInput,
    RegisterUserInput,
    TokenPairOutput,
    UserOutput,
)
from src.modules.auth.domain.entities import SystemRole, User
from src.modules.auth.domain.exceptions import (
    InactiveUserError,
    InvalidCredentialsError,
    InvalidTokenError,
    UserAlreadyExistsError,
)
from src.modules.auth.domain.repositories import UserRepository
from src.shared.repository import UnitOfWorkProtocol


def _to_output(user: User) -> UserOutput:
    return UserOutput(
        id=str(user.id),
        email=user.email,
        full_name=user.full_name,
        roles=[r.value for r in user.roles],
        is_active=user.is_active,
    )


class RegisterUserUseCase:
    def __init__(self, users: UserRepository, uow: UnitOfWorkProtocol) -> None:
        self._users = users
        self._uow = uow

    async def execute(self, data: RegisterUserInput) -> UserOutput:
        existing = await self._users.get_by_email(
            data.email, organization_id=data.organization_id
        )
        if existing is not None:
            raise UserAlreadyExistsError(data.email)

        user = User(
            email=data.email,
            hashed_password=hash_password(data.password),
            full_name=data.full_name,
            organization_id=data.organization_id,
            roles=[SystemRole.VIEWER],
        )
        async with self._uow:
            await self._users.add(user)
            await self._uow.commit()
        return _to_output(user)


class AuthenticateUserUseCase:
    """Validates credentials and issues an access/refresh token pair."""

    def __init__(self, users: UserRepository, jwt_service: JWTService) -> None:
        self._users = users
        self._jwt_service = jwt_service

    async def execute(self, data: AuthenticateInput) -> TokenPairOutput:
        user = await self._users.get_by_email(
            data.email, organization_id=data.organization_id
        )
        if user is None or not verify_password(data.password, user.hashed_password):
            raise InvalidCredentialsError()
        if not user.is_active:
            raise InactiveUserError()

        roles = [r.value for r in user.roles]
        return TokenPairOutput(
            access_token=self._jwt_service.issue_access_token(str(user.id), roles),
            refresh_token=self._jwt_service.issue_refresh_token(str(user.id), roles),
        )


class RefreshTokenUseCase:
    """Exchanges a valid refresh token for a new access token.

    Re-reads the user so a role change or deactivation since the refresh
    token was issued is honored immediately, rather than trusting stale
    claims embedded in the refresh token itself.
    """

    def __init__(self, users: UserRepository, jwt_service: JWTService) -> None:
        self._users = users
        self._jwt_service = jwt_service

    async def execute(self, refresh_token: str) -> TokenPairOutput:
        payload = self._jwt_service.decode(refresh_token)
        if payload.token_type is not TokenType.REFRESH:
            raise InvalidTokenError("Provided token is not a refresh token")

        user = await self._users.get_by_id(uuid.UUID(payload.subject))
        if user is None or not user.is_active:
            raise InvalidTokenError("User no longer active")

        roles = [r.value for r in user.roles]
        return TokenPairOutput(
            access_token=self._jwt_service.issue_access_token(str(user.id), roles),
            refresh_token=self._jwt_service.issue_refresh_token(str(user.id), roles),
        )
