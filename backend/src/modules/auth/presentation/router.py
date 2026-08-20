"""Auth HTTP endpoints. Every route is documented for OpenAPI/Swagger via
`summary`, `description`, and `responses` so `/docs` is a complete reference
without hand-written API docs elsewhere.
"""
from __future__ import annotations

from fastapi import APIRouter, Depends, status

from src.modules.auth.application.dto import (
    AuthenticateInput,
    RegisterUserInput,
)
from src.modules.auth.application.use_cases import (
    AuthenticateUserUseCase,
    RefreshTokenUseCase,
    RegisterUserUseCase,
)
from src.modules.auth.domain.entities import User
from src.modules.auth.presentation.dependencies import (
    get_authenticate_use_case,
    get_current_user,
    get_refresh_use_case,
    get_register_use_case,
)
from src.modules.auth.presentation.schemas import (
    LoginRequest,
    RefreshRequest,
    RegisterRequest,
    TokenPairResponse,
    UserResponse,
)

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
    description=(
        "Creates a new user within an organization (tenant) with the "
        "default `viewer` role. Emails are unique per `organization_id`, "
        "not globally — the same email may belong to users in two "
        "different organizations."
    ),
    responses={409: {"description": "A user with this email already exists in the organization"}},
)
async def register(
    body: RegisterRequest,
    use_case: RegisterUserUseCase = Depends(get_register_use_case),
) -> UserResponse:
    output = await use_case.execute(
        RegisterUserInput(
            email=body.email,
            password=body.password,
            full_name=body.full_name,
            organization_id=body.organization_id,
        )
    )
    return UserResponse(**output.__dict__)


@router.post(
    "/login",
    response_model=TokenPairResponse,
    summary="Authenticate and obtain a JWT access/refresh token pair",
    responses={401: {"description": "Invalid credentials or inactive account"}},
)
async def login(
    body: LoginRequest,
    use_case: AuthenticateUserUseCase = Depends(get_authenticate_use_case),
) -> TokenPairResponse:
    output = await use_case.execute(
        AuthenticateInput(
            email=body.email, password=body.password, organization_id=body.organization_id
        )
    )
    return TokenPairResponse(**output.__dict__)


@router.post(
    "/refresh",
    response_model=TokenPairResponse,
    summary="Exchange a refresh token for a new token pair",
    responses={401: {"description": "Invalid, expired, or non-refresh token"}},
)
async def refresh(
    body: RefreshRequest,
    use_case: RefreshTokenUseCase = Depends(get_refresh_use_case),
) -> TokenPairResponse:
    output = await use_case.execute(body.refresh_token)
    return TokenPairResponse(**output.__dict__)


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get the currently authenticated user",
)
async def me(user: User = Depends(get_current_user)) -> UserResponse:
    return UserResponse(
        id=str(user.id),
        email=user.email,
        full_name=user.full_name,
        roles=[r.value for r in user.roles],
        is_active=user.is_active,
    )
