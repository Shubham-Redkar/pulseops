class AppException(Exception):
    """Base exception for application errors."""


class NotFoundError(AppException):
    """Raised when a requested resource does not exist."""


class ConflictError(AppException):
    """Raised when an operation conflicts with existing state."""


class UserNotFoundError(NotFoundError):
    pass


class TeamNotFoundError(NotFoundError):
    pass


class ServiceNotFoundError(NotFoundError):
    pass


class IncidentNotFoundError(NotFoundError):
    pass
