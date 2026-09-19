from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from .base import IDMixin, ORMBaseSchema, TimeStampMixin


class ServiceBase(BaseModel):
    """
    Common fields shared by service request and response schemas.
    """

    name: str = Field(
        min_length=1,
        max_length=255,
        description="Name of the service.",
        examples=["payment-service"],
    )

    description: str = Field(
        min_length=1,
        max_length=5000,
        description="Detailed description of the service.",
        examples=["Handles payment processing and transaction management."],
    )

    team_id: UUID = Field(
        examples=["66dee2d6-f869-4152-9fb9-8461c73506ce"],
        description="Unique identifier for the team.",
    )


class CreateServiceRequest(ServiceBase):
    """
    Request body for creating a service.
    """

    model_config = ConfigDict(
        extra="forbid",
        json_schema_extra={
            "example": {
                "name": "payment-service",
                "description": "Handles payment processing and transaction management.",
                "team_id": "66dee2d6-f869-4152-9fb9-8461c73506ce",
            }
        },
    )


class UpdateServiceRequest(BaseModel):
    """
    Request body for partially updating a service.
    Only fields provided by the client will be updated.
    """

    model_config = ConfigDict(
        extra="forbid",
        json_schema_extra={
            "example": {
                "name": "payment-service",
                "description": "Handles payment processing and transaction management.",
                "team_id": "66dee2d6-f869-4152-9fb9-8461c73506ce",
            }
        },
    )

    name: str | None = Field(
        default=None,
        min_length=1,
        max_length=255,
        description="Name of the service.",
        examples=["payment-service"],
    )

    description: str | None = Field(
        default=None,
        min_length=1,
        max_length=5000,
        description="Detailed description of the service.",
        examples=["Handles payment processing and transaction management."],
    )

    team_id: UUID | None = Field(
        default=None,
        examples=["66dee2d6-f869-4152-9fb9-8461c73506ce"],
        description="Unique identifier for the team.",
    )


class ServiceResponse(
    ORMBaseSchema,
    IDMixin,
    TimeStampMixin,
    ServiceBase,
):
    """
    Response representation of a service.
    """
