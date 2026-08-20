"""Password hashing and JWT issuance/verification.

Kept in `core` (not inside the `auth` module) because other modules — e.g.
`datasources`, for encrypting stored connection secrets — reuse primitives
from here. Business rules about *who* is allowed to do *what* stay in the
`auth` module's domain layer; this file only implements the cryptographic
mechanics.
"""
from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from enum import StrEnum

import jwt
from passlib.context import CryptContext

from src.config import Settings

_pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(plain_password: str) -> str:
    return _pwd_context.hash(plain_password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return _pwd_context.verify(plain_password, hashed_password)


class TokenType(StrEnum):
    ACCESS = "access"
    REFRESH = "refresh"


@dataclass(frozen=True, slots=True)
class TokenPayload:
    subject: str          # user id
    token_type: TokenType
    roles: tuple[str, ...]
    jti: str
    expires_at: datetime


class JWTService:
    """Thin wrapper around PyJWT so use cases depend on an interface, not
    the raw library. Injected via `Depends(get_jwt_service)` in presentation.
    """

    def __init__(self, settings: Settings) -> None:
        self._secret = settings.jwt_secret_key
        self._algorithm = settings.jwt_algorithm
        self._access_ttl = timedelta(minutes=settings.access_token_expire_minutes)
        self._refresh_ttl = timedelta(days=settings.refresh_token_expire_days)

    def issue_access_token(self, user_id: str, roles: list[str]) -> str:
        return self._issue(user_id, roles, TokenType.ACCESS, self._access_ttl)

    def issue_refresh_token(self, user_id: str, roles: list[str]) -> str:
        return self._issue(user_id, roles, TokenType.REFRESH, self._refresh_ttl)

    def _issue(
        self, user_id: str, roles: list[str], token_type: TokenType, ttl: timedelta
    ) -> str:
        now = datetime.now(UTC)
        payload = {
            "sub": user_id,
            "type": token_type.value,
            "roles": roles,
            "jti": str(uuid.uuid4()),
            "iat": now,
            "exp": now + ttl,
        }
        return jwt.encode(payload, self._secret, algorithm=self._algorithm)

    def decode(self, token: str) -> TokenPayload:
        raw = jwt.decode(token, self._secret, algorithms=[self._algorithm])
        return TokenPayload(
            subject=raw["sub"],
            token_type=TokenType(raw["type"]),
            roles=tuple(raw.get("roles", [])),
            jti=raw["jti"],
            expires_at=datetime.fromtimestamp(raw["exp"], tz=UTC),
        )
