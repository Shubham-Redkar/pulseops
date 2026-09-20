from typing import TypedDict
from uuid import UUID

from ..schemas.base import CleanString


class ServiceUpdateData(TypedDict, total=False):
    name: CleanString
    description: CleanString | None
    team_id: UUID | None
