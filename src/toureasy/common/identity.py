from __future__ import annotations

import uuid
from dataclasses import dataclass
from typing import Any, Generic, TypeVar

from toureasy.common.errors.common_error_codes import CommonErrorCodes
from toureasy.common.errors.domain_error import DomainError, InvariantViolationError
from toureasy.common.result import Result, failure, success



TModel = TypeVar("TModel")


@dataclass(frozen=True, slots=True, order=True)
class Id(Generic[TModel]):

    value: uuid.UUID

    def __post_init__(self) -> None:
        if not isinstance(self.value, uuid.UUID) or self.value.int == 0:
            raise InvariantViolationError("Id cannot be empty.")

    @classmethod
    def new(cls) -> Id[TModel]:
        return cls(uuid.uuid4())

    @classmethod
    def create(cls, value: uuid.UUID) -> Result[Id[TModel], DomainError]:
        if value.int == 0:
            return failure(DomainError.validation("Id cannot be empty.", code=CommonErrorCodes.INVALID_ID))
        return success(cls(value))

    @classmethod
    def parse(cls, value: str | None) -> Result[Id[TModel], DomainError]:
        if value is None or not value.strip():
            return failure(DomainError.bad_request("Id is required.", code=CommonErrorCodes.INVALID_ID))
        try:
            parsed = uuid.UUID(value.strip())
        except ValueError:
            return failure(DomainError.bad_request("Id is invalid.", code=CommonErrorCodes.INVALID_ID))
        if parsed.int == 0:
            return failure(DomainError.bad_request("Id is invalid.", code=CommonErrorCodes.INVALID_ID))
        return success(cls(parsed))

    @classmethod
    def from_id(cls, other: Id[Any]) -> Id[TModel]:
        return cls(other.value)

    def __str__(self) -> str:
        return self.value.hex
