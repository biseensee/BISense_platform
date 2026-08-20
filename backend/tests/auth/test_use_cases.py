"""Unit tests for the auth use cases against an in-memory fake repository —
no database, no FastAPI. This is the payoff of keeping use cases decoupled
from SQLAlchemy: `RegisterUserUseCase`/`AuthenticateUserUseCase` are tested
purely through the `UserRepository` Protocol.
"""
from __future__ import annotations

import uuid

import pytest

from src.config import Settings
from src.core.security import JWTService
from src.modules.auth.application.dto import AuthenticateInput, RegisterUserInput
from src.modules.auth.application.use_cases import AuthenticateUserUseCase, RegisterUserUseCase
from src.modules.auth.domain.entities import User
from src.modules.auth.domain.exceptions import InvalidCredentialsError, UserAlreadyExistsError


class FakeUserRepository:
    def __init__(self) -> None:
        self._by_id: dict[uuid.UUID, User] = {}

    async def get_by_id(self, user_id: uuid.UUID) -> User | None:
        return self._by_id.get(user_id)

    async def get_by_email(self, email: str, *, organization_id: str) -> User | None:
        return next(
            (
                u
                for u in self._by_id.values()
                if u.email == email and u.organization_id == organization_id
            ),
            None,
        )

    async def add(self, user: User) -> None:
        self._by_id[user.id] = user

    async def update(self, user: User) -> None:
        self._by_id[user.id] = user

    async def list_by_organization(self, organization_id: str) -> list[User]:
        return [u for u in self._by_id.values() if u.organization_id == organization_id]


class FakeUnitOfWork:
    async def __aenter__(self) -> "FakeUnitOfWork":
        return self

    async def __aexit__(self, exc_type: object, exc: object, tb: object) -> None:
        pass

    async def commit(self) -> None:
        pass

    async def rollback(self) -> None:
        pass


@pytest.fixture
def settings() -> Settings:
    return Settings(
        jwt_secret_key="test-secret",
        datasource_encryption_key="w4uWZ6zC0m1z9m3v3s2f5s9k1c3v3w4u3W5z1c9v3W0=",
    )


async def test_register_user_creates_and_persists() -> None:
    repo = FakeUserRepository()
    use_case = RegisterUserUseCase(repo, FakeUnitOfWork())

    output = await use_case.execute(
        RegisterUserInput(
            email="ada@example.com",
            password="supersecret1",
            full_name="Ada Lovelace",
            organization_id="org-1",
        )
    )

    assert output.email == "ada@example.com"
    assert output.roles == ["viewer"]
    stored = await repo.get_by_email("ada@example.com", organization_id="org-1")
    assert stored is not None
    assert stored.hashed_password != "supersecret1"  # never stored in plaintext


async def test_register_user_rejects_duplicate_email_in_same_org() -> None:
    repo = FakeUserRepository()
    use_case = RegisterUserUseCase(repo, FakeUnitOfWork())
    data = RegisterUserInput(
        email="ada@example.com", password="supersecret1", full_name="Ada", organization_id="org-1"
    )
    await use_case.execute(data)

    with pytest.raises(UserAlreadyExistsError):
        await use_case.execute(data)


async def test_authenticate_user_rejects_wrong_password(settings: Settings) -> None:
    repo = FakeUserRepository()
    await RegisterUserUseCase(repo, FakeUnitOfWork()).execute(
        RegisterUserInput(
            email="ada@example.com",
            password="supersecret1",
            full_name="Ada",
            organization_id="org-1",
        )
    )
    use_case = AuthenticateUserUseCase(repo, JWTService(settings))

    with pytest.raises(InvalidCredentialsError):
        await use_case.execute(
            AuthenticateInput(email="ada@example.com", password="wrong", organization_id="org-1")
        )


async def test_authenticate_user_issues_token_pair_on_success(settings: Settings) -> None:
    repo = FakeUserRepository()
    await RegisterUserUseCase(repo, FakeUnitOfWork()).execute(
        RegisterUserInput(
            email="ada@example.com",
            password="supersecret1",
            full_name="Ada",
            organization_id="org-1",
        )
    )
    use_case = AuthenticateUserUseCase(repo, JWTService(settings))

    tokens = await use_case.execute(
        AuthenticateInput(email="ada@example.com", password="supersecret1", organization_id="org-1")
    )

    assert tokens.access_token
    assert tokens.refresh_token
    assert tokens.access_token != tokens.refresh_token
