from datetime import datetime
from decimal import Decimal
from typing import Annotated
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, StringConstraints

from .base import CleanString, IDMixin, ORMBaseSchema, TimestampMixin
from .enums import Environment, IncidentSeverity

AlertSource = Annotated[
    CleanString,
    StringConstraints(
        max_length=255,
    ),
]

AlertMetric = Annotated[
    CleanString,
    StringConstraints(
        max_length=255,
    ),
]


class CreateAlertRequest(BaseModel):
    """
    Request body for ingesting an alert from an external monitoring system.
    """

    model_config = ConfigDict(
        extra="forbid",
        json_schema_extra={
            "example": {
                "service_id": "66dee2d6-f869-4152-9fb9-8461c73506ce",
                "environment": "production",
                "severity": "critical",
                "source": "prometheus",
                "metric": "error_rate",
                "value": 18.7,
                "threshold": 5.0,
                "timestamp": "2026-09-29T10:00:00Z",
            }
        },
    )

    service_id: UUID = Field(
        description="Unique identifier of the affected service.",
        examples=["66dee2d6-f869-4152-9fb9-8461c73506ce"],
    )

    environment: Environment = Field(
        description="Environment where the alert occurred.",
        examples=["production"],
    )

    severity: IncidentSeverity = Field(
        description="Severity level of the alert.",
        examples=["critical"],
    )

    source: AlertSource = Field(
        description="Monitoring or alerting system that generated the alert.",
        examples=["prometheus"],
    )

    metric: AlertMetric = Field(
        description="Metric that triggered the alert.",
        examples=["error_rate"],
    )

    value: Decimal = Field(
        description="Observed metric value.",
        examples=[18.7],
    )

    threshold: Decimal = Field(
        description="Configured threshold that was exceeded.",
        examples=[5.0],
    )

    timestamp: datetime = Field(
        description="Timestamp when the monitoring system generated the alert.",
        examples=["2026-09-29T10:00:00Z"],
    )


class AlertResponse(
    ORMBaseSchema,
    IDMixin,
    TimestampMixin,
):
    """
    Response representation of an ingested alert.
    """

    service_id: UUID = Field(
        description="Unique identifier of the affected service.",
        examples=["66dee2d6-f869-4152-9fb9-8461c73506ce"],
    )

    incident_id: UUID | None = Field(
        default=None,
        description="Unique identifier of the incident associated with the alert.",
        examples=["66dee2d6-f869-4152-9fb9-8461c73506ce"],
    )

    environment: Environment = Field(
        description="Environment where the alert occurred.",
        examples=["production"],
    )

    severity: IncidentSeverity = Field(
        description="Severity level of the alert.",
        examples=["critical"],
    )

    source: AlertSource = Field(
        description="Monitoring or alerting system that generated the alert.",
        examples=["prometheus"],
    )

    metric: AlertMetric = Field(
        description="Metric that triggered the alert.",
        examples=["error_rate"],
    )

    value: Decimal = Field(
        description="Observed metric value.",
        examples=[18.7],
    )

    threshold: Decimal = Field(
        description="Configured threshold that was exceeded.",
        examples=[5.0],
    )

    timestamp: datetime = Field(
        description="Timestamp when the monitoring system generated the alert.",
        examples=["2026-09-29T10:00:00Z"],
    )

    fingerprint: CleanString = Field(
        description="Deterministic fingerprint used for alert correlation and deduplication.",
        examples=["a8d5c3f1e7b9..."],
    )
