"""Application-layer DTOs — the contract between use cases and presentation.

Kept separate from `presentation/schemas.py` (Pydantic, HTTP-shaped) so the
use cases don't depend on FastAPI/Pydantic request/response conventions.
Plain dataclasses are enough here since there's no wire (de)serialization.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class RegisterUserInput:
    email: str
    password: str
    full_name: str
    organization_id: str


@dataclass(frozen=True, slots=True)
class AuthenticateInput:
    email: str
    password: str
    organization_id: str


@dataclass(frozen=True, slots=True)
class TokenPairOutput:
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


@dataclass(frozen=True, slots=True)
class UserOutput:
    id: str
    email: str
    full_name: str
    roles: list[str]
    is_active: bool
