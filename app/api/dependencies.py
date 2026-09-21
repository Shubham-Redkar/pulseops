from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from ..db.dependencies import get_db
from ..repositories.incident_repository import IncidentRepository
from ..repositories.service_repository import ServiceRepository
from ..repositories.team_repository import TeamRepository
from ..repositories.user_repository import UserRepository
from ..services.incident_service import IncidentService
from ..services.service_service import ServiceManager
from ..services.team_service import TeamService
from ..services.user_service import UserService

SessionDep = Annotated[
    AsyncSession,
    Depends(get_db),
]


def get_team_service(
    session: SessionDep,
) -> TeamService:
    """
    Provide a team service with its database dependencies.
    """
    return TeamService(
        session=session,
        repository=TeamRepository(session),
    )


TeamServiceDep = Annotated[
    TeamService,
    Depends(get_team_service),
]


def get_service_manager(
    session: SessionDep,
) -> ServiceManager:
    """
    Provide a service manager with its database dependencies.
    """
    return ServiceManager(
        session=session,
        repository=ServiceRepository(session),
    )


ServiceManagerDep = Annotated[
    ServiceManager,
    Depends(get_service_manager),
]


def get_user_service(
    session: SessionDep,
) -> UserService:
    """
    Provide a user service with its database dependencies.
    """
    return UserService(
        session=session,
        repository=UserRepository(session),
    )


UserServiceDep = Annotated[
    UserService,
    Depends(get_user_service),
]


def get_incident_service(
    session: SessionDep,
) -> IncidentService:
    """
    Provide a incident service with its database dependencies.
    """
    return IncidentService(
        session=session,
        repository=IncidentRepository(session),
    )


IncidentServiceDep = Annotated[
    IncidentService,
    Depends(get_incident_service),
]
