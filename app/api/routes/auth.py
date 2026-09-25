from fastapi import APIRouter

from ...schemas.auth import LoginRequest, RefreshTokenRequest, RegisterRequest, TokenResponse
from ...schemas.user import UserResponse
from ..dependencies import AuthServiceDep, CurrentUserDep

router = APIRouter(
    prefix="/auth",
    tags=["Auth"],
)


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: CurrentUserDep) -> UserResponse:
    return UserResponse.model_validate(current_user)


@router.post("/register", response_model=UserResponse)
async def register(
    data: RegisterRequest,
    auth_service: AuthServiceDep,
) -> UserResponse:
    return await auth_service.register(data)


@router.post("/login", response_model=TokenResponse)
async def login(
    data: LoginRequest,
    auth_service: AuthServiceDep,
) -> TokenResponse:
    return await auth_service.login(data)


@router.post("/refresh", response_model=TokenResponse)
async def refresh(
    data: RefreshTokenRequest,
    auth_service: AuthServiceDep,
) -> TokenResponse:
    return await auth_service.refresh(data)
