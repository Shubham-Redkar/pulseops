from typing import Annotated
from uuid import UUID

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.exceptions import InvalidTokenError, UnauthorizedError
from ..core.security import decode_and_validate_access_token
from ..db.dependencies import get_db
from ..db.models.user import User
from ..repositories.incident_repository import IncidentRepository
from ..repositories.refresh_token_repository import RefreshTokenRepository
from ..repositories.service_repository import ServiceRepository
from ..repositories.team_repository import TeamRepository
from ..repositories.user_repository import UserRepository
from ..services.auth_service import AuthService
from ..services.incident_service import IncidentService
from ..services.service_service import ServiceManager
from ..services.team_service import TeamService
from ..services.user_service import UserService

SessionDep = Annotated[
    AsyncSession,
    Depends(get_db),
]

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/v1/auth/login",
)


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    session: SessionDep,
) -> User:
    payload = decode_and_validate_access_token(token)

    try:
        user_id = UUID(payload["sub"])
    except ValueError as exc:
        raise InvalidTokenError() from exc

    repository = UserRepository(session)

    async with session.begin():
        user = await repository.get_by_id(user_id)

        if user is None:
            raise UnauthorizedError()

    return user


CurrentUserDep = Annotated[
    User,
    Depends(get_current_user),
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
    Provide an user service with its database dependencies.
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
    Provide an incident service with its database dependencies.
    """
    return IncidentService(
        session=session,
        repository=IncidentRepository(session),
    )


IncidentServiceDep = Annotated[
    IncidentService,
    Depends(get_incident_service),
]


def get_auth_service(
    session: SessionDep,
) -> AuthService:
    """
    Provide an auth service with its database dependencies.
    """
    return AuthService(
        session=session,
        user_repository=UserRepository(session),
        refresh_token_repository=RefreshTokenRepository(session),
    )


AuthServiceDep = Annotated[
    AuthService,
    Depends(get_auth_service),
]
