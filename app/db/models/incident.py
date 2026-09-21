from datetime import UTC, datetime
from enum import Enum
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlalchemy import DateTime, ForeignKey, String, text
from sqlalchemy.dialects.postgresql import ENUM
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.schemas.enums import Environment, IncidentSeverity

from .base import Base

if TYPE_CHECKING:
    from .service import Service


def enum_values(enum_class: type[Enum]) -> list[str]:
    return [member.value for member in enum_class]


class Incident(Base):
    """
    Database model representing an incident affecting a service.
    """

    __tablename__ = "incidents"

    id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )

    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        index=True,
    )

    description: Mapped[str] = mapped_column(
        String(5000),
        nullable=False,
    )

    service_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey(
            "services.id",
            ondelete="RESTRICT",
        ),
        nullable=False,
        index=True,
    )

    environment: Mapped[Environment] = mapped_column(
        ENUM(
            Environment,
            name="environment_enum",
            create_type=False,
            values_callable=enum_values,
        ),
        nullable=False,
    )

    severity: Mapped[IncidentSeverity] = mapped_column(
        ENUM(
            IncidentSeverity,
            name="incident_severity_enum",
            create_type=False,
            values_callable=enum_values,
        ),
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
        onupdate=lambda: datetime.now(UTC),
    )

    service: Mapped["Service"] = relationship(
        back_populates="incidents",
    )
