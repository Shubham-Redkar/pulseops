from fastapi import (
    APIRouter,
    Request,
    Response,
    status,
)

from ...core.rate_limit import (
    check_forgot_password_rate_limit,
    check_login_ip_rate_limit,
    check_login_username_rate_limit,
    check_password_reset_rate_limit,
    check_refresh_rate_limit,
    check_verify_email_rate_limit,
)
from ...schemas.auth import (
    ChangePasswordRequest,
    ForgotPasswordRequest,
    LoginRequest,
    RefreshTokenRequest,
    RegisterRequest,
    ResetPasswordRequest,
    TokenResponse,
    VerifyEmailRequest,
)
from ...schemas.user import UserResponse
from ..dependencies import (
    AuthServiceDep,
    CurrentTokenPayloadDep,
    CurrentUserDep,
    RedisStoreDep,
)
from ..utils import set_rate_limit_headers

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
    request: Request,
    response: Response,
    data: LoginRequest,
    auth_service: AuthServiceDep,
    redis_store: RedisStoreDep,
) -> TokenResponse:
    client_ip = request.client.host if request.client else "unknown"

    ip_limit, ip_remaining, ip_reset = await check_login_ip_rate_limit(
        redis_store,
        client_ip,
    )

    username_limit, username_remaining, username_reset = await check_login_username_rate_limit(
        redis_store,
        data.username,
    )

    set_rate_limit_headers(
        response,
        limit=min(ip_limit, username_limit),
        remaining=min(ip_remaining, username_remaining),
        reset=max(ip_reset, username_reset),
    )

    return await auth_service.login(
        data,
        client_ip,
    )


@router.post(
    "/refresh",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
)
async def refresh(
    request: Request,
    response: Response,
    data: RefreshTokenRequest,
    auth_service: AuthServiceDep,
    redis_store: RedisStoreDep,
) -> TokenResponse:
    client_ip = request.client.host if request.client else "unknown"

    limit, remaining, reset = await check_refresh_rate_limit(
        redis_store,
        client_ip,
    )

    set_rate_limit_headers(
        response,
        limit=limit,
        remaining=remaining,
        reset=reset,
    )

    return await auth_service.refresh(
        data,
        client_ip,
    )


@router.post(
    "/logout",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def logout(
    data: RefreshTokenRequest,
    token_payload: CurrentTokenPayloadDep,
    auth_service: AuthServiceDep,
) -> None:
    await auth_service.logout(
        data,
        token_payload,
    )


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
    request: Request,
    response: Response,
    data: ForgotPasswordRequest,
    auth_service: AuthServiceDep,
    redis_store: RedisStoreDep,
) -> None:
    client_ip = request.client.host if request.client else "unknown"

    limit, remaining, reset = await check_forgot_password_rate_limit(
        redis_store,
        client_ip,
    )

    set_rate_limit_headers(
        response,
        limit=limit,
        remaining=remaining,
        reset=reset,
    )

    await auth_service.forgot_password(
        data,
        client_ip,
    )


@router.post(
    "/reset-password",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def reset_password(
    request: Request,
    response: Response,
    data: ResetPasswordRequest,
    auth_service: AuthServiceDep,
    redis_store: RedisStoreDep,
) -> None:
    client_ip = request.client.host if request.client else "unknown"

    limit, remaining, reset = await check_password_reset_rate_limit(
        redis_store,
        client_ip,
    )

    set_rate_limit_headers(
        response,
        limit=limit,
        remaining=remaining,
        reset=reset,
    )

    await auth_service.reset_password(
        data,
        client_ip,
    )


@router.post(
    "/verify-email",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def verify_email(
    request: Request,
    response: Response,
    data: VerifyEmailRequest,
    auth_service: AuthServiceDep,
    redis_store: RedisStoreDep,
) -> None:
    client_ip = request.client.host if request.client else "unknown"

    limit, remaining, reset = await check_verify_email_rate_limit(
        redis_store,
        client_ip,
    )

    set_rate_limit_headers(
        response,
        limit=limit,
        remaining=remaining,
        reset=reset,
    )

    await auth_service.verify_email(
        data,
        client_ip,
    )
