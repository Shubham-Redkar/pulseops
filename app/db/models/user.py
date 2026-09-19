from datetime import UTC, datetime
from enum import Enum
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlalchemy import DateTime, ForeignKey, String, text
from sqlalchemy.dialects.postgresql import ENUM
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.schemas.enums import UserRole

from .base import Base

if TYPE_CHECKING:
    from .team import Team


def enum_values(enum_class: type[Enum]) -> list[str]:
    return [member.value for member in enum_class]


class User(Base):
    __tablename__ = "users"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)

    username: Mapped[str] = mapped_column(String(50), nullable=False, unique=True, index=True)

    email: Mapped[str] = mapped_column(String(254), nullable=False, unique=True, index=True)

    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)

    role: Mapped[UserRole] = mapped_column(
        ENUM(UserRole, name="user_role_enum", create_type=False, values_callable=enum_values),
        nullable=False,
    )

    team_id: Mapped[UUID | None] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("teams.id", ondelete="SET NULL"), nullable=True, index=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=text("CURRENT_TIMESTAMP")
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
        onupdate=lambda: datetime.now(UTC),
    )

    team: Mapped["Team | None"] = relationship(back_populates="users")
