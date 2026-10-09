from __future__ import annotations
from dataclasses import dataclass

from toureasy.common.errors.domain_error import DomainError
from toureasy.common.result import Result, failure, success
from toureasy.domain.agency.errors import AnnouncementErrorCodes



@dataclass(frozen=True)
class PhotoGallery:
    photos: tuple[str, ...]          # storage keys or URLs, order = display order

    @classmethod
    def create(cls, photos: list[str]) -> Result[PhotoGallery]:
        cleaned = tuple(p.strip() for p in (photos or []) if p and p.strip())
        if not cleaned:                       # can't publish a tour with no photos
            return failure(DomainError.validation(
                "At least one photo is required", AnnouncementErrorCodes.GALLERY_EMPTY))
        if len(cleaned) > 20:
            return failure(DomainError.validation(
                "Too many photos (max 20)", AnnouncementErrorCodes.GALLERY_TOO_LARGE))
        return success(cls(cleaned))

    @property
    def cover(self) -> str:
        return self.photos[0]