from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from ..db.models.password_reset_token import PasswordResetToken


class PasswordResetTokenRepository:
    """
    Repository for password reset token persistence operations.
    """

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, password_reset_token: PasswordResetToken) -> PasswordResetToken:
        self.session.add(password_reset_token)

        await self.session.flush()

        return password_reset_token

    async def get_by_hash(
        self,
        token_hash: str,
    ) -> PasswordResetToken | None:
        stmt = select(PasswordResetToken).where(
            PasswordResetToken.token_hash == token_hash,
        )

        return await self.session.scalar(stmt)

    async def invalidate_unused_for_user(
        self,
        user_id: UUID,
    ) -> None:
        now = datetime.now(UTC)

        await self.session.execute(
            update(PasswordResetToken)
            .where(
                PasswordResetToken.user_id == user_id,
                PasswordResetToken.used_at.is_(None),
                PasswordResetToken.expires_at > now,
            )
            .values(used_at=now)
        )
