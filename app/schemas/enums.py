from enum import StrEnum


class IncidentSeverity(StrEnum):
    """Severity of an incident."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class Environment(StrEnum):
    """Deployment environment where the incident occurred."""

    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"


class UserRole(StrEnum):
    """"""

    ADMIN = "admin"
    ANALYST = "analyst"
    VIEWER = "viewer"
