from uuid import UUID

from fastapi import APIRouter

from ...schemas.user import CreateUserRequest, UpdateUserRequest, UserResponse
from ...services.user_service import user_service

router = APIRouter(prefix="/users", tags=["Users"])


@router.post("", response_model=UserResponse)
async def create_user(user_data: CreateUserRequest) -> UserResponse:
    return await user_service.create_user(user_data)


@router.get("", response_model=list[UserResponse])
async def get_users() -> list[UserResponse]:
    return await user_service.get_users()


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: UUID) -> UserResponse:
    return await user_service.get_user(user_id)


@router.patch("/{user_id}", response_model=UserResponse)
async def update_user(user_id: UUID, user_data: UpdateUserRequest) -> UserResponse:
    return await user_service.update_user(user_id, user_data)


@router.delete("/{user_id}", status_code=204)
async def delete_user(user_id: UUID) -> None:
    return await user_service.delete_user(user_id)
