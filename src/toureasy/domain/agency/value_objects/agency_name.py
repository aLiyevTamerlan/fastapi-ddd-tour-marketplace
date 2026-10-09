from __future__ import annotations

from dataclasses import dataclass
from typing import ClassVar

from toureasy.common.errors.domain_error import DomainError, InvariantViolationError
from toureasy.common.result import Result, failure, success
from toureasy.domain.agency.errors import AgencyErrorCodes
from toureasy.domain.agency.value_objects._text import normalize_text



@dataclass(frozen=True, slots=True)
class AgencyName:
    MAXIMUM_LENGTH: ClassVar[int] = 200

    value: str

    def __post_init__(self) -> None:
        if not isinstance(self.value, str) or self.value != normalize_text(self.value) or self._validate(self.value):
            raise InvariantViolationError(f"Invalid AgencyName {self.value!r}. Use AgencyName.create().")

    @classmethod
    def create(cls, value: str | None) -> Result[AgencyName, DomainError]:
        normalized = normalize_text(value or "")
        error = cls._validate(normalized)
        if error is not None:
            return failure(error)
        return success(cls(normalized))

    def __str__(self) -> str:
        return self.value
    
    @classmethod
    def _validate(cls, normalized: str) -> DomainError | None:
        if not normalized:
            return DomainError.bad_request("Agency name is required.", code=AgencyErrorCodes.INVALID_AGENCY_NAME)
        if len(normalized) > AgencyName.MAXIMUM_LENGTH:
            return DomainError.validation(
                f"Agency name cannot exceed {AgencyName.MAXIMUM_LENGTH} characters.",
                code=AgencyErrorCodes.INVALID_AGENCY_NAME,
            )
        return None
