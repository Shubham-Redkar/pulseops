from typing import TypedDict
from uuid import UUID

from ..schemas.base import CleanString
from ..schemas.enums import UserRole


class UserUpdateData(TypedDict, total=False):
    username: CleanString

    email: str | None

    role: UserRole | None

    team_id: UUID | None
