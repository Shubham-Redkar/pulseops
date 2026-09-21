"""add incident environment and severity

Revision ID: 944f2d5ed58b
Revises: af930607ea02
Create Date: 2026-09-21 12:24:19.105136

"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "944f2d5ed58b"
down_revision: str | Sequence[str] | None = "af930607ea02"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    environment_enum = postgresql.ENUM(
        "development",
        "staging",
        "production",
        name="environment_enum",
    )
    environment_enum.create(op.get_bind(), checkfirst=True)

    incident_severity_enum = postgresql.ENUM(
        "low",
        "medium",
        "high",
        "critical",
        name="incident_severity_enum",
    )
    incident_severity_enum.create(op.get_bind(), checkfirst=True)

    op.add_column(
        "incidents",
        sa.Column(
            "environment",
            environment_enum,
            nullable=False,
        ),
    )

    op.add_column(
        "incidents",
        sa.Column(
            "severity",
            incident_severity_enum,
            nullable=False,
        ),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("incidents", "severity")
    op.drop_column("incidents", "environment")

    incident_severity_enum = postgresql.ENUM(
        "low",
        "medium",
        "high",
        "critical",
        name="incident_severity_enum",
    )
    incident_severity_enum.drop(op.get_bind(), checkfirst=True)

    environment_enum = postgresql.ENUM(
        "development",
        "staging",
        "production",
        name="environment_enum",
    )
    environment_enum.drop(op.get_bind(), checkfirst=True)
