from __future__ import annotations

from enum import Enum, unique


@unique
class AgencyStatus(Enum):
    """Lifecycle of an agency. A new agency waits for admin verification (PRD A-02, D-01)."""

    PENDING_VERIFICATION = "PendingVerification"
    ACTIVE = "Active"
    REJECTED = "Rejected"
    SUSPENDED = "Suspended"

    @classmethod
    def from_name(cls, name: str) -> AgencyStatus:
        return cls(name)


class AnnouncementStatus(Enum):
    PUBLISHED = "published"
    ARCHIVED  = "archived"