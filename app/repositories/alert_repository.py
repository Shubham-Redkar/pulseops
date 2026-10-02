from collections.abc import Sequence
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..db.models.alert import Alert


class AlertRepository:
    """
    Repository for alert persistence operations.
    """

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(
        self,
        alert: Alert,
    ) -> Alert:
        self.session.add(alert)

        await self.session.flush()

        return alert

    async def get_by_id(
        self,
        alert_id: UUID,
    ) -> Alert | None:
        stmt = select(Alert).where(Alert.id == alert_id)

        return await self.session.scalar(stmt)

    async def get_by_fingerprint(
        self,
        fingerprint: str,
    ) -> Alert | None:
        stmt = (
            select(Alert)
            .where(Alert.fingerprint == fingerprint)
            .order_by(Alert.created_at.desc())
            .limit(1)
        )

        return await self.session.scalar(stmt)

    async def list_by_incident(
        self,
        incident_id: UUID,
    ) -> Sequence[Alert]:
        stmt = select(Alert).where(Alert.incident_id == incident_id).order_by(Alert.timestamp.asc())

        result = await self.session.scalars(stmt)

        return result.all()
