"""Pydantic request/response schemas — the HTTP contract for /auth.

These are intentionally separate from `application/dto.py`: a breaking
change to the wire format (e.g. renaming a JSON field for a mobile client)
should never force a change to the use case's internal DTO, and vice versa.
"""
from __future__ import annotations

from pydantic import BaseModel, EmailStr, Field


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    full_name: str = Field(min_length=1, max_length=200)
    organization_id: str = Field(min_length=1, max_length=64)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str
    organization_id: str


class RefreshRequest(BaseModel):
    refresh_token: str


class TokenPairResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    id: str
    email: str
    full_name: str
    roles: list[str]
    is_active: bool
