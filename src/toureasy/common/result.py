"""Result / UnitResult - the Python counterpart of CSharpFunctionalExtensions.

Expected failures (validation, conflicts, unavailable dependencies) travel as values,
not exceptions, so every failure path is explicit in signatures and easy to test.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any, Generic, TypeVar, cast, final

T = TypeVar("T")
E = TypeVar("E")
U = TypeVar("U")


class ResultAccessError(RuntimeError):
    """Raised when reading ``value`` of a failure or ``error`` of a success."""


@final
class Result(Generic[T, E]):
    __slots__ = ("_error", "_is_success", "_value")

    def __init__(self, *, is_success: bool, value: T | None = None, error: E | None = None) -> None:
        if not is_success and error is None:
            raise ValueError("A failed result requires an error.")
        self._is_success = is_success
        self._value = value
        self._error = error

    @property
    def is_success(self) -> bool:
        return self._is_success

    @property
    def is_failure(self) -> bool:
        return not self._is_success

    @property
    def value(self) -> T:
        if not self._is_success:
            raise ResultAccessError(f"Cannot access the value of a failed result: {self._error!r}")
        return cast(T, self._value)

    @property
    def error(self) -> E:
        if self._is_success:
            raise ResultAccessError("Cannot access the error of a successful result.")
        return cast(E, self._error)

    def map(self, mapper: Callable[[T], U]) -> Result[U, E]:
        if self.is_failure:
            return Result(is_success=False, error=self._error)
        return Result(is_success=True, value=mapper(self.value))

    def bind(self, binder: Callable[[T], Result[U, E]]) -> Result[U, E]:
        if self.is_failure:
            return Result(is_success=False, error=self._error)
        return binder(self.value)

    def __repr__(self) -> str:
        if self._is_success:
            return f"Success({self._value!r})"
        return f"Failure({self._error!r})"

def success(value: T) -> Result[T, Any]:
    return Result(is_success=True, value=value)


def failure(error: E) -> Result[Any, E]:
    return Result(is_success=False, error=error)
