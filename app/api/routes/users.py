from uuid import UUID

from fastapi import APIRouter, Query, status

from ...schemas.base import PaginatedResponse
from ...schemas.user import (
    CreateUserRequest,
    UpdateUserRequest,
    UserResponse,
)
from ..dependencies import CurrentUserDep, UserServiceDep

router = APIRouter(
    prefix="/users",
    tags=["Users"],
)


@router.post(
    "",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_user(
    current_user: CurrentUserDep,
    user_data: CreateUserRequest,
    user_service: UserServiceDep,
) -> UserResponse:
    return await user_service.create_user(user_data)


@router.get(
    "/{user_id}",
    response_model=UserResponse,
)
async def get_user(
    current_user: CurrentUserDep,
    user_id: UUID,
    user_service: UserServiceDep,
) -> UserResponse:
    return await user_service.get_user(user_id)


@router.get(
    "",
    response_model=PaginatedResponse[UserResponse],
)
async def get_users(
    current_user: CurrentUserDep,
    user_service: UserServiceDep,
    limit: int = Query(
        default=20,
        ge=1,
        le=100,
        description="Maximum number of users to return.",
    ),
    offset: int = Query(
        default=0,
        ge=0,
        description="Number of users to skip.",
    ),
) -> PaginatedResponse[UserResponse]:
    return await user_service.get_users(
        limit=limit,
        offset=offset,
    )


@router.patch(
    "/{user_id}",
    response_model=UserResponse,
)
async def update_user(
    current_user: CurrentUserDep,
    user_id: UUID,
    user_data: UpdateUserRequest,
    user_service: UserServiceDep,
) -> UserResponse:
    return await user_service.update_user(
        user_id,
        user_data,
    )


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_user(
    current_user: CurrentUserDep,
    user_id: UUID,
    user_service: UserServiceDep,
) -> None:
    await user_service.delete_user(user_id)
