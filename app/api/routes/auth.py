from fastapi import APIRouter, status

from ...schemas.auth import (
    ChangePasswordRequest,
    ForgotPasswordRequest,
    LoginRequest,
    RefreshTokenRequest,
    RegisterRequest,
    ResetPasswordRequest,
    TokenResponse,
)
from ...schemas.user import UserResponse
from ..dependencies import AuthServiceDep, CurrentUserDep

router = APIRouter(
    prefix="/auth",
    tags=["Auth"],
)


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: CurrentUserDep) -> UserResponse:
    return UserResponse.model_validate(current_user)


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
async def register(
    data: RegisterRequest,
    auth_service: AuthServiceDep,
) -> UserResponse:
    return await auth_service.register(data)


@router.post(
    "/login",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
)
async def login(
    data: LoginRequest,
    auth_service: AuthServiceDep,
) -> TokenResponse:
    return await auth_service.login(data)


@router.post(
    "/refresh",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
)
async def refresh(
    data: RefreshTokenRequest,
    auth_service: AuthServiceDep,
) -> TokenResponse:
    return await auth_service.refresh(data)


@router.post(
    "/logout",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def logout(
    data: RefreshTokenRequest,
    auth_service: AuthServiceDep,
) -> None:
    await auth_service.logout(data)


@router.post(
    "/change-password",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def change_password(
    current_user: CurrentUserDep,
    data: ChangePasswordRequest,
    auth_service: AuthServiceDep,
) -> None:
    await auth_service.change_password(current_user, data)


@router.post(
    "/forgot-password",
    status_code=status.HTTP_202_ACCEPTED,
)
async def forgot_password(
    data: ForgotPasswordRequest,
    auth_service: AuthServiceDep,
) -> None:
    await auth_service.forgot_password(data)


@router.post(
    "/reset-password",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def reset_password(
    data: ResetPasswordRequest,
    auth_service: AuthServiceDep,
) -> None:
    await auth_service.reset_password(data)
