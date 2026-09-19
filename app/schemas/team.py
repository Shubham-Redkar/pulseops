from pydantic import BaseModel, ConfigDict, Field

from .base import IDMixin, ORMBaseSchema, TimeStampMixin


class TeamBase(BaseModel):
    """
    Common fields shared by team request and response schemas.
    """

    name: str = Field(
        min_length=1,
        max_length=255,
        description="Name of the team.",
        examples=["Payments Team"],
    )

    description: str = Field(
        min_length=1,
        max_length=5000,
        description="Detailed description of what the team is about.",
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
    Only fields provided by the client will be updated.
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

    name: str | None = Field(
        default=None,
        min_length=1,
        max_length=255,
        description="Name of the team.",
        examples=["Payments Team"],
    )

    description: str | None = Field(
        default=None,
        min_length=1,
        max_length=5000,
        description="Detailed description of what the team is about.",
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
