from enum import StrEnum


class ErrorCode(StrEnum):
    """
    Application error codes exposed by the API.
    """

    VALIDATION_ERROR = "VALIDATION_ERROR"
    NOT_FOUND = "NOT_FOUND"
    CONFLICT = "CONFLICT"
    INTERNAL_ERROR = "INTERNAL_ERROR"
