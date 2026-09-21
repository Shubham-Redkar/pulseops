from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from .base import CleanString, IDMixin, ORMBaseSchema, TimestampMixin
from .enums import Environment, IncidentSeverity


class IncidentBase(BaseModel):
    """
    Common fields shared by incident request and response schemas.
    """

    title: CleanString = Field(
        min_length=1,
        max_length=255,
        description="Short title describing the incident.",
        examples=["Payment API error rate elevated"],
    )

    description: CleanString = Field(
        min_length=1,
        max_length=5000,
        description="Detailed description of what is happening.",
        examples=["Error rate exceeded the production threshold."],
    )

    service_id: UUID = Field(
        description="Unique identifier of the affected service.",
        examples=["66dee2d6-f869-4152-9fb9-8461c73506ce"],
    )

    environment: Environment = Field(
        description="Environment where the incident occurred.",
        examples=["production"],
    )

    severity: IncidentSeverity = Field(
        description="Severity level indicating the impact of the incident.",
        examples=["critical"],
    )


class CreateIncidentRequest(IncidentBase):
    """
    Request body for creating an incident.
    """

    model_config = ConfigDict(
        extra="forbid",
        json_schema_extra={
            "example": {
                "title": "Payment API error rate elevated",
                "description": "Error rate exceeded the production threshold.",
                "service_id": "66dee2d6-f869-4152-9fb9-8461c73506ce",
                "environment": "production",
                "severity": "critical",
            }
        },
    )


class UpdateIncidentRequest(BaseModel):
    """
    Request body for partially updating an incident.
    Only fields provided by the client will be updated.
    """

    model_config = ConfigDict(
        extra="forbid",
        json_schema_extra={
            "example": {
                "title": "Payment API error rate elevated",
                "description": "Error rate exceeded the production threshold.",
                "service_id": "66dee2d6-f869-4152-9fb9-8461c73506ce",
                "environment": "production",
                "severity": "critical",
            }
        },
    )

    title: CleanString | None = Field(
        default=None,
        min_length=1,
        max_length=255,
        description="Short title describing the incident.",
        examples=["Payment API error rate elevated"],
    )

    description: CleanString | None = Field(
        default=None,
        min_length=1,
        max_length=5000,
        description="Detailed description of what is happening.",
        examples=["Error rate exceeded the production threshold."],
    )

    service_id: UUID | None = Field(
        default=None,
        description="Unique identifier of the affected service.",
        examples=["66dee2d6-f869-4152-9fb9-8461c73506ce"],
    )

    environment: Environment | None = Field(
        default=None,
        description="Environment where the incident occurred.",
        examples=["production"],
    )

    severity: IncidentSeverity | None = Field(
        default=None,
        description="Severity level indicating the impact of the incident.",
        examples=["critical"],
    )


class IncidentResponse(
    ORMBaseSchema,
    IDMixin,
    TimestampMixin,
    IncidentBase,
):
    """
    Response representation of an incident.
    """
