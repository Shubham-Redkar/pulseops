from pydantic import BaseModel, ConfigDict, Field

from .base import CleanString, IDMixin, ORMBaseSchema, TimeStampMixin


class TeamBase(BaseModel):
    """
    Common fields shared by team request and response schemas.
    """

    name: CleanString = Field(
        min_length=1,
        max_length=255,
        description="Name of the team.",
        examples=["Payments Team"],
    )

    description: CleanString | None = Field(
        default=None,
        max_length=2000,
        description="Description of the team.",
        examples=["Owns payment processing services and ensures reliable payment operations."],
    )


class CreateTeamRequest(TeamBase):
    """
    Request body for creating a team.
    """

    model_config = ConfigDict(
        extra="forbid",
        json_schema_extra={
            "example": {
                "name": "Payments Team",
                "description": (
                    "Owns payment processing services and ensures reliable payment operations."
                ),
            }
        },
    )


class UpdateTeamRequest(BaseModel):
    """
    Request body for partially updating a team.

    Only fields explicitly provided by the client will be updated.
    """

    model_config = ConfigDict(
        extra="forbid",
        json_schema_extra={
            "example": {
                "name": "Payments Team",
                "description": (
                    "Owns payment processing services and ensures reliable payment operations."
                ),
            }
        },
    )

    name: CleanString | None = Field(
        default=None,
        min_length=1,
        max_length=255,
        description="Name of the team.",
        examples=["Payments Team"],
    )

    description: CleanString | None = Field(
        default=None,
        max_length=2000,
        description="Description of the team.",
        examples=["Owns payment processing services and ensures reliable payment operations."],
    )


class TeamResponse(
    ORMBaseSchema,
    IDMixin,
    TimeStampMixin,
    TeamBase,
):
    """
    Response representation of a team.
    """
