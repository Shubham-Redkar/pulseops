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


class IncidentStatus(StrEnum):
    """Current lifecycle state of an incident."""

    OPEN = "open"
    ACKNOWLEDGED = "acknowledged"
    RESOLVED = "resolved"


class UserRole(StrEnum):
    """Role assigned to a user."""

    ADMIN = "admin"
    ANALYST = "analyst"
    VIEWER = "viewer"
