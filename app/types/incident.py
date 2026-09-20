from typing import TypedDict
from uuid import UUID

from ..schemas.base import CleanString
from ..schemas.enums import Environment, IncidentSeverity


class IncidentUpdateData(TypedDict, total=False):
    title: CleanString
    description: CleanString | None
    service_id: UUID | None
    environment: Environment
    severity: IncidentSeverity
