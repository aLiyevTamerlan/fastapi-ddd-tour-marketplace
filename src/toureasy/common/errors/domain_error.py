from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from typing import Protocol

from toureasy.common.errors.error_type import ErrorType



class IDomainError(Protocol):
    """Read-only error contract used by Application ports and the API."""

    @property
    def code(self) -> str: ...

    @property
    def error_message(self) -> str: ...

    @property
    def error_type(self) -> ErrorType: ...

    @property
    def errors(self) -> tuple[str, ...] | None: ...


class InvariantViolationError(ValueError):
    """Raised when code bypasses a factory and tries to build an invalid domain object.

    Expected failures use ``Result``; this exception signals a programming error.
    """


@dataclass(frozen=True, slots=True)
class DomainError:
    code: str
    error_message: str
    error_type: ErrorType
    errors: tuple[str, ...] | None = None

    @classmethod
    def conflict(cls, message: str | None = None, code: str | None = None) -> DomainError:
        return cls(
            _or(code, "conflict"),
            _or(message, "The data provided conflicts with existing data."),
            ErrorType.CONFLICT,
        )

    @classmethod
    def not_found(cls, message: str | None = None, code: str | None = None) -> DomainError:
        return cls(_or(code, "not_found"), _or(message, "The requested item could not be found."), ErrorType.NOT_FOUND)

    @classmethod
    def bad_request(cls, message: str | None = None, code: str | None = None) -> DomainError:
        return cls(_or(code, "bad_request"), _or(message, "Invalid request or parameters."), ErrorType.BAD_REQUEST)

    @classmethod
    def validation(
        cls,
        message: str | None = None,
        errors: Sequence[str] | None = None,
        code: str | None = None,
    ) -> DomainError:
        return cls(
            _or(code, "validation_failed"),
            _or(message, "Validation failed."),
            ErrorType.VALIDATION,
            tuple(errors) if errors is not None else None,
        )

    @classmethod
    def unexpected(cls, message: str | None = None, code: str | None = None) -> DomainError:
        return cls(_or(code, "unexpected"), _or(message, "Unexpected error happened."), ErrorType.UNEXPECTED)

    @classmethod
    def unavailable(cls, message: str | None = None, code: str | None = None) -> DomainError:
        return cls(
            _or(code, "unavailable"), _or(message, "A required dependency is unavailable."), ErrorType.UNAVAILABLE
        )

    @classmethod
    def too_many_requests(cls, message: str | None = None, code: str | None = None) -> DomainError:
        return cls(
            _or(code, "too_many_requests"),
            _or(message, "Rate or capacity limit exceeded."),
            ErrorType.TOO_MANY_REQUESTS,
        )


def _or(value: str | None, default: str) -> str:
    return default if value is None else value
