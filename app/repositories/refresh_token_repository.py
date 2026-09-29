from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from ..db.models.refresh_token import RefreshToken


class RefreshTokenRepository:
    """
    Repository for refresh token persistence operations.
    """

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(
        self,
        refresh_token: RefreshToken,
    ) -> RefreshToken:
        self.session.add(refresh_token)

        await self.session.flush()

        return refresh_token

    async def get_by_hash(
        self,
        token_hash: str,
    ) -> RefreshToken | None:
        stmt = select(RefreshToken).where(RefreshToken.token_hash == token_hash)

        return await self.session.scalar(stmt)

    async def revoke(
        self,
        refresh_token: RefreshToken,
    ) -> None:
        refresh_token.revoked_at = datetime.now(UTC)
        await self.session.flush()

    async def revoke_all_for_user(
        self,
        user_id: UUID,
    ) -> None:
        stmt = (
            update(RefreshToken)
            .where(
                RefreshToken.user_id == user_id,
                RefreshToken.revoked_at.is_(None),
            )
            .values(revoked_at=datetime.now(UTC))
        )

        await self.session.execute(stmt)
        await self.session.flush()

    async def delete_expired_or_revoked(self) -> int:
        stmt = (
            delete(RefreshToken)
            .where(
                (RefreshToken.expires_at <= datetime.now(UTC))
                | (RefreshToken.revoked_at.is_not(None))
            )
            .returning(RefreshToken.id)
        )

        result = await self.session.execute(stmt)

        return len(result.all())
