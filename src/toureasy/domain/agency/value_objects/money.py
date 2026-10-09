# domain/common/value_objects/money.py
from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, InvalidOperation

from toureasy.common.errors.domain_error import DomainError, IDomainError
from toureasy.common.result import Result, failure, success
from toureasy.domain.agency.errors import MoneyErrorCodes


_TWO_PLACES = Decimal("0.01")


@dataclass(frozen=True)
class Money:
    """A monetary amount in a single currency. Non-negative, at most two decimal places,
    currency as a 3-letter upper-case code (e.g. ``AZN``). Shared across the domain —
    announcement price, deposit, balance, and any future reservation amount."""

    amount: Decimal
    currency: str

    @classmethod
    def create(
        cls,
        amount: Decimal | int | str | float | None,
        currency: str | None,
    ) -> Result[Money, IDomainError]:
        # --- amount ---
        if amount is None:
            return failure(DomainError.validation(
                "Amount is required.", MoneyErrorCodes.AMOUNT_REQUIRED))
        try:
            # route float through str so 0.1 doesn't become 0.1000000000000000055…
            value = Decimal(str(amount)) if isinstance(amount, float) else Decimal(amount)
        except (InvalidOperation, TypeError, ValueError):
            return failure(DomainError.validation(
                "Amount is not a valid number.", MoneyErrorCodes.AMOUNT_INVALID))

        if not value.is_finite():
            return failure(DomainError.validation(
                "Amount must be a finite number.", MoneyErrorCodes.AMOUNT_INVALID))
        if value < 0:
            return failure(DomainError.validation(
                "Amount cannot be negative.", MoneyErrorCodes.AMOUNT_NEGATIVE))
        if value != value.quantize(_TWO_PLACES):          # reject, do NOT round
            return failure(DomainError.validation(
                "Amount cannot have more than two decimal places.",
                MoneyErrorCodes.AMOUNT_TOO_MANY_DECIMALS))

        # --- currency ---
        code = (currency or "").strip().upper()
        if len(code) != 3 or not code.isalpha():
            return failure(DomainError.validation(
                "Currency must be a 3-letter code such as AZN.",
                MoneyErrorCodes.CURRENCY_INVALID))

        return success(cls(value, code))

    @property
    def is_zero(self) -> bool:
        return self.amount == 0

    def __str__(self) -> str:
        return f"{self.amount:.2f} {self.currency}"