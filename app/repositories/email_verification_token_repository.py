from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from ..db.models.email_verification_token import EmailVerificationToken


class EmailVerificationTokenRepository:
    """
    Repository for email verification token persistence operations.
    """

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, verification_token: EmailVerificationToken) -> EmailVerificationToken:
        self.session.add(verification_token)

        await self.session.flush()

        return verification_token

    async def get_by_hash(self, token_hash: str) -> EmailVerificationToken | None:
        stmt = select(EmailVerificationToken).where(
            EmailVerificationToken.token_hash == token_hash,
        )

        return await self.session.scalar(stmt)

    async def invalidate_unused_for_user(self, user_id: UUID) -> None:
        now = datetime.now(UTC)

        await self.session.execute(
            update(EmailVerificationToken)
            .where(
                EmailVerificationToken.user_id == user_id,
                EmailVerificationToken.used_at.is_(None),
                EmailVerificationToken.expires_at > now,
            )
            .values(used_at=now)
        )
