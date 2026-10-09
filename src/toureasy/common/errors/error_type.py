from enum import Enum, unique


@unique
class ErrorType(Enum):
    """Error categories. The API maps each one to an HTTP status (see BaseController)."""

    CONFLICT = "Conflict"
    NOT_FOUND = "NotFound"
    BAD_REQUEST = "BadRequest"
    VALIDATION = "Validation"
    UNEXPECTED = "Unexpected"
    UNAVAILABLE = "Unavailable"
    TOO_MANY_REQUESTS = "TooManyRequests"
