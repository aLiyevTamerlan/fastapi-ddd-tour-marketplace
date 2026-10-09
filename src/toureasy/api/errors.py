from __future__ import annotations

from typing import Any, TypeVar

from fastapi import HTTPException, status

from toureasy.common.errors.domain_error import IDomainError
from toureasy.common.errors.error_type import ErrorType
from toureasy.common.result import Result

T = TypeVar("T")

# The only place where error categories become HTTP status codes.
_STATUS_BY_ERROR_TYPE: dict[ErrorType, int] = {
    ErrorType.CONFLICT: status.HTTP_409_CONFLICT,
    ErrorType.NOT_FOUND: status.HTTP_404_NOT_FOUND,
    ErrorType.BAD_REQUEST: status.HTTP_400_BAD_REQUEST,
    ErrorType.VALIDATION: status.HTTP_400_BAD_REQUEST,
    ErrorType.UNEXPECTED: status.HTTP_500_INTERNAL_SERVER_ERROR,
    ErrorType.UNAVAILABLE: status.HTTP_503_SERVICE_UNAVAILABLE,
    ErrorType.TOO_MANY_REQUESTS: status.HTTP_429_TOO_MANY_REQUESTS,
}


def unwrap(result: Result[T, Any]) -> T:
    """Return the value of a successful result, or raise an ``HTTPException`` for a failed one.

    Response body on failure: ``{"detail": {"code": "...", "message": "..."}}``.
    """
    if result.is_success:
        return result.value
    error: IDomainError = result.error
    raise HTTPException(
        status_code=_STATUS_BY_ERROR_TYPE[error.error_type],
        detail={"code": error.code, "message": error.error_message},
    )
