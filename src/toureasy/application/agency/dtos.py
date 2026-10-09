from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict

from toureasy.domain.agency.agency import Agency


class AgencyDto(BaseModel):
    """What the application layer hands to the API. Plain values only, no domain objects."""

    model_config = ConfigDict(frozen=True)

    id: str
    name: str
    contact_email: str
    status: str
    rejection_reason: str | None
    created_at_utc: datetime
    last_modified_at_utc: datetime

    @classmethod
    def from_entity(cls, agency: Agency) -> AgencyDto:
        return cls(
            id=str(agency.id),
            name=agency.name.value,
            contact_email=agency.contact_email.value,
            status=agency.status.value,
            rejection_reason=agency.rejection_reason,
            created_at_utc=agency.created_at_utc,
            last_modified_at_utc=agency.last_modified_at_utc,
        )
