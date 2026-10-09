from __future__ import annotations

import uuid
from datetime import datetime
from typing import ClassVar

from toureasy.common.entity import Entity
from toureasy.common.errors.domain_error import DomainError, IDomainError
from toureasy.common.identity import Id
from toureasy.common.result import Result, failure, success
from toureasy.domain.agency.enums import AgencyStatus
from toureasy.domain.agency.errors import AgencyErrorCodes
from toureasy.domain.agency.value_objects._text import normalize_text
from toureasy.domain.agency.value_objects.agency_name import AgencyName
from toureasy.domain.agency.value_objects.contact_email import ContactEmail


class Agency(Entity["Agency"]):
    """A tour agency. It owns its own profile and status; its announcements are separate entities
    that reference it by ``agency_id`` (see ``Announcement``).

    Status transitions::

        PENDING_VERIFICATION --verify--> ACTIVE <--reactivate-- SUSPENDED
                 |                         |                        ^
                 +--reject--> REJECTED     +--------suspend---------+
    """

    REJECTION_REASON_MAXIMUM_LENGTH: ClassVar[int] = 500

    def __init__(
        self,
        agency_id: Id[Agency],
        name: AgencyName,
        contact_email: ContactEmail,
        status: AgencyStatus,
        created_at: datetime,
        last_modified_at: datetime,
        rejection_reason: str | None = None,
    ) -> None:
        super().__init__(agency_id, created_at, last_modified_at)
        self._name = name
        self._contact_email = contact_email
        self._status = status
        self._rejection_reason = rejection_reason

    # ---- factories -------------------------------------------------------------------------

    @classmethod
    def create(cls, name: str | None, contact_email: str | None, now: datetime) -> Result[Agency, IDomainError]:
        """A newly registered agency waits for admin verification before it can publish (PRD A-02)."""
        name_result = AgencyName.create(name)
        if name_result.is_failure:
            return failure(name_result.error)

        email_result = ContactEmail.create(contact_email)
        if email_result.is_failure:
            return failure(email_result.error)

        return success(
            cls(Id.new(), name_result.value, email_result.value, AgencyStatus.PENDING_VERIFICATION, now, now)
        )

    @classmethod
    def rehydrate(
        cls,
        *,
        agency_id: uuid.UUID,
        name: str,
        contact_email: str,
        status: str,
        rejection_reason: str | None,
        created_at: datetime,
        last_modified_at: datetime,
    ) -> Agency:
        """Rebuild an agency loaded from storage. Business rules are not re-run; value object
        constructors only reject corrupted data (``InvariantViolationError``)."""
        return cls(
            Id(agency_id),
            AgencyName(name),
            ContactEmail(contact_email),
            AgencyStatus(status),
            created_at,
            last_modified_at,
            rejection_reason,
        )

    # ---- properties ------------------------------------------------------------------------

    @property
    def name(self) -> AgencyName:
        return self._name

    @property
    def contact_email(self) -> ContactEmail:
        return self._contact_email

    @property
    def status(self) -> AgencyStatus:
        return self._status

    @property
    def rejection_reason(self) -> str | None:
        return self._rejection_reason

    @property
    def can_publish(self) -> bool:
        return self._status is AgencyStatus.ACTIVE

    # ---- behaviour -------------------------------------------------------------------------

    def ensure_can_publish(self) -> Result[None, IDomainError]:
        """Rule used by the application layer before it publishes an announcement for this agency."""
        if self._status is AgencyStatus.SUSPENDED:
            return failure(
                DomainError.conflict(
                    "A suspended agency cannot publish announcements.", AgencyErrorCodes.AGENCY_SUSPENDED
                )
            )
        if not self.can_publish:
            return failure(
                DomainError.conflict(
                    "Only a verified agency can publish announcements.", AgencyErrorCodes.AGENCY_NOT_ACTIVE
                )
            )
        return success(None)

    def rename(self, name: str | None, now: datetime) -> Result[None, IDomainError]:
        name_result = AgencyName.create(name)
        if name_result.is_failure:
            return failure(name_result.error)
        self._name = name_result.value
        self._last_modified_at_utc = now
        return success(None)

    def change_contact_email(self, contact_email: str | None, now: datetime) -> Result[None, IDomainError]:
        email_result = ContactEmail.create(contact_email)
        if email_result.is_failure:
            return failure(email_result.error)
        self._contact_email = email_result.value
        self._last_modified_at_utc = now
        return success(None)

    def verify(self, now: datetime) -> Result[None, IDomainError]:
        """Admin confirmed the agency's registration and tax ID (PRD D-01)."""
        if self._status is not AgencyStatus.PENDING_VERIFICATION:
            return failure(
                DomainError.conflict(
                    "Only an agency awaiting verification can be verified.",
                    AgencyErrorCodes.AGENCY_NOT_PENDING_VERIFICATION,
                )
            )
        self._status = AgencyStatus.ACTIVE
        self._last_modified_at_utc = now
        return success(None)

    def reject(self, reason: str | None, now: datetime) -> Result[None, IDomainError]:
        """Admin declined the registration; the reason is sent to the agency (PRD D-01)."""
        normalized = normalize_text(reason or "")
        if not normalized:
            return failure(
                DomainError.validation("Rejection reason is required.", code=AgencyErrorCodes.INVALID_REJECTION_REASON)
            )
        if len(normalized) > self.REJECTION_REASON_MAXIMUM_LENGTH:
            return failure(
                DomainError.validation(
                    f"Rejection reason cannot exceed {self.REJECTION_REASON_MAXIMUM_LENGTH} characters.",
                    code=AgencyErrorCodes.INVALID_REJECTION_REASON,
                )
            )
        if self._status is not AgencyStatus.PENDING_VERIFICATION:
            return failure(
                DomainError.conflict(
                    "Only an agency awaiting verification can be rejected.",
                    AgencyErrorCodes.AGENCY_NOT_PENDING_VERIFICATION,
                )
            )
        self._status = AgencyStatus.REJECTED
        self._rejection_reason = normalized
        self._last_modified_at_utc = now
        return success(None)

    def suspend(self, now: datetime) -> Result[None, IDomainError]:
        if self._status is AgencyStatus.SUSPENDED:
            return failure(
                DomainError.conflict("Agency is already suspended.", AgencyErrorCodes.AGENCY_ALREADY_SUSPENDED)
            )
        if self._status is not AgencyStatus.ACTIVE:
            return failure(
                DomainError.conflict("Only an active agency can be suspended.", AgencyErrorCodes.AGENCY_NOT_ACTIVE)
            )
        self._status = AgencyStatus.SUSPENDED
        self._last_modified_at_utc = now
        return success(None)

    def reactivate(self, now: datetime) -> Result[None, IDomainError]:
        if self._status is AgencyStatus.ACTIVE:
            return failure(DomainError.conflict("Agency is already active.", AgencyErrorCodes.AGENCY_ALREADY_ACTIVE))
        if self._status is not AgencyStatus.SUSPENDED:
            return failure(
                DomainError.conflict(
                    "Only a suspended agency can be reactivated.", AgencyErrorCodes.AGENCY_NOT_SUSPENDED
                )
            )
        self._status = AgencyStatus.ACTIVE
        self._last_modified_at_utc = now
        return success(None)
