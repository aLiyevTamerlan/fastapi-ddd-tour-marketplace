from __future__ import annotations
from dataclasses import dataclass

from toureasy.common.errors.domain_error import DomainError
from toureasy.common.result import Result, failure, success
from toureasy.domain.agency.errors import AnnouncementErrorCodes

@dataclass(frozen=True)
class ItineraryItem:
    order: int
    title: str
    detail: str


@dataclass(frozen=True)
class Itinerary:
    items: tuple[ItineraryItem, ...]

    @classmethod
    def create(cls, items: list[ItineraryItem]) -> "Result[Itinerary]":
        if not items:
            return failure(DomainError.validation(
                "Itinerary needs at least one stop", AnnouncementErrorCodes.ITINERARY_EMPTY))
        ordered = tuple(sorted(items, key=lambda i: i.order))
        return success(cls(ordered))