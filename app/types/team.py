from typing import TypedDict

from ..schemas.base import CleanString


class TeamUpdateData(TypedDict, total=False):
    name: CleanString
    description: CleanString | None
