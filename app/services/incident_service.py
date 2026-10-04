import secrets
from typing import cast
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from ..core.config import settings
from ..core.exceptions import IncidentNotFoundError, ServiceUnavailableError
from ..core.redis import RedisStore
from ..core.types import IncidentUpdateData
from ..db.models.incident import Incident
from ..repositories.incident_repository import IncidentRepository
from ..schemas.base import PaginatedResponse
from ..schemas.incident import (
    CreateIncidentRequest,
    IncidentResponse,
    UpdateIncidentRequest,
)


class IncidentService:
    """
    Manage incident business operations.
    """

    def __init__(
        self,
        session: AsyncSession,
        repository: IncidentRepository,
        redis_store: RedisStore,
    ) -> None:
        self.session = session
        self.repository = repository
        self.redis_store = redis_store

    async def create_incident(
        self,
        incident_data: CreateIncidentRequest,
    ) -> IncidentResponse:
        incident = Incident(
            **incident_data.model_dump(),
        )

        async with self.session.begin():
            incident = await self.repository.create(incident)

        return IncidentResponse.model_validate(incident)

    async def get_incident(
        self,
        incident_id: UUID,
    ) -> IncidentResponse:
        cache_key = f"{settings.redis_key_prefix}:incident:{incident_id}"
        lock_key = f"{settings.redis_key_prefix}:incident:lock:{incident_id}"

        cached_incident = await self.redis_store.get(cache_key)

        if cached_incident is not None:
            return IncidentResponse.model_validate_json(cached_incident)

        lock_token = secrets.token_urlsafe(32)

        lock_acquired = await self.redis_store.acquire_lock(
            lock_key,
            lock_token,
            ex=5,
        )

        if not lock_acquired:
            raise ServiceUnavailableError("Incident is currently being loaded. Please try again.")

        try:
            cached_incident = await self.redis_store.get(cache_key)

            if cached_incident is not None:
                return IncidentResponse.model_validate_json(cached_incident)

            if (incident := await self.repository.get_by_id(incident_id)) is None:
                raise IncidentNotFoundError(incident_id)

            response = IncidentResponse.model_validate(incident)

            await self.redis_store.set(
                cache_key,
                response.model_dump_json(),
                ex=300,
            )

            return response

        finally:
            await self.redis_store.release_lock(
                lock_key,
                lock_token,
            )

    async def get_incidents(
        self,
        limit: int,
        offset: int,
    ) -> PaginatedResponse[IncidentResponse]:
        incidents, total = await self.repository.get_all(
            limit=limit,
            offset=offset,
        )

        return PaginatedResponse(
            items=[IncidentResponse.model_validate(incident) for incident in incidents],
            limit=limit,
            offset=offset,
            total=total,
        )

    async def update_incident(
        self,
        incident_id: UUID,
        incident_data: UpdateIncidentRequest,
    ) -> IncidentResponse:
        update_data = cast(
            IncidentUpdateData,
            incident_data.model_dump(exclude_unset=True),
        )

        async with self.session.begin():
            if (
                incident := await self.repository.update(
                    incident_id,
                    update_data,
                )
            ) is None:
                raise IncidentNotFoundError(incident_id)

            await self.redis_store.delete(
                f"{settings.redis_key_prefix}:incident:{incident_id}",
            )

        return IncidentResponse.model_validate(incident)

    async def delete_incident(
        self,
        incident_id: UUID,
    ) -> None:
        async with self.session.begin():
            deleted = await self.repository.delete(incident_id)

            if not deleted:
                raise IncidentNotFoundError(incident_id)

            await self.redis_store.delete(
                f"{settings.redis_key_prefix}:incident:{incident_id}",
            )
