from __future__ import annotations
from dataclasses import dataclass
from datetime import time

from toureasy.common.errors.domain_error import DomainError
from toureasy.common.result import Result, failure, success
from toureasy.domain.agency.errors import AnnouncementErrorCodes



@dataclass(frozen=True)
class MeetingPoint:
    address: str
    meet_time: time

    @classmethod
    def create(cls, address: str, meet_time: time) -> Result[MeetingPoint]:
        address = (address or "").strip()
        if not address:
            return failure(DomainError.validation(
                "Meeting point is required", AnnouncementErrorCodes.MEETING_POINT_EMPTY))
        return success(cls(address, meet_time))