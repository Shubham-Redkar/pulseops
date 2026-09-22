from uuid import UUID


class AppException(Exception):
    """
    Base exception for expected application errors.
    """

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


class NotFoundError(AppException):
    """
    Raised when a requested resource does not exist.
    """


class ConflictError(AppException):
    """
    Raised when an operation conflicts with existing state.
    """

    def __init__(self, detail: str):
        self.detail = detail


class UserNotFoundError(NotFoundError):
    """
    Raised when a user does not exist.
    """

    def __init__(self, user_id: UUID) -> None:
        super().__init__(f"User '{user_id}' was not found.")


class TeamNotFoundError(NotFoundError):
    """
    Raised when a team does not exist.
    """

    def __init__(self, team_id: UUID) -> None:
        super().__init__(f"Team '{team_id}' was not found.")


class ServiceNotFoundError(NotFoundError):
    """
    Raised when a service does not exist.
    """

    def __init__(self, service_id: UUID) -> None:
        super().__init__(f"Service '{service_id}' was not found.")


class IncidentNotFoundError(NotFoundError):
    """
    Raised when an incident does not exist.
    """

    def __init__(self, incident_id: UUID) -> None:
        super().__init__(f"Incident '{incident_id}' was not found.")
