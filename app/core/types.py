from typing import TypedDict
from uuid import UUID

from ..schemas.base import CleanString
from ..schemas.enums import Environment, IncidentSeverity, UserRole


class IncidentUpdateData(TypedDict, total=False):
    title: CleanString
    description: CleanString | None
    service_id: UUID | None
    environment: Environment
    severity: IncidentSeverity


class ServiceUpdateData(TypedDict, total=False):
    name: CleanString
    description: CleanString | None
    team_id: UUID | None


class TeamUpdateData(TypedDict, total=False):
    name: CleanString
    description: CleanString | None


class UserUpdateData(TypedDict, total=False):
    username: CleanString

    email: str | None

    role: UserRole | None

    team_id: UUID | None
