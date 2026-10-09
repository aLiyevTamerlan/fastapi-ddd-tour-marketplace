# domain/announcement/announcement.py
from __future__ import annotations

from datetime import date, datetime, time
from decimal import Decimal

from toureasy.common.entity import Entity
from toureasy.common.errors.domain_error import DomainError, IDomainError
from toureasy.common.identity import Id
from toureasy.common.result import Result, failure, success
from toureasy.domain.agency.agency import Agency
from toureasy.domain.agency.enums import AnnouncementStatus
from toureasy.domain.agency.errors import AnnouncementErrorCodes
from toureasy.domain.agency.value_objects.date_range import DateRange
from toureasy.domain.agency.value_objects.inclusions import Inclusions
from toureasy.domain.agency.value_objects.itinerary import Itinerary, ItineraryItem
from toureasy.domain.agency.value_objects.meeting_point import MeetingPoint
from toureasy.domain.agency.value_objects.money import Money
from toureasy.domain.agency.value_objects.photo_gallery import PhotoGallery



class Announcement(Entity["Announcement"]):
    """A tour listing (elan). It belongs to one agency, referenced by ``agency_id`` — the
    ``Agency`` is a separate entity, never held here. Contact details (T-12) and the agency's
    other tours (T-13) are resolved through that id by the application layer, not stored on the
    announcement. ``seats_left`` (T-10) is derived from a reservation count supplied by the
    service; sharing (T-14) needs only the id."""

    def __init__(
        self,
        announcement_id: Id[Announcement],
        agency_id: Id[Agency],
        title: str,
        description: str,
        gallery: PhotoGallery,
        itinerary: Itinerary,
        inclusions: Inclusions,
        meeting_point: MeetingPoint,
        dates: DateRange,

        price_per_person: Money,
        capacity: int,
        status: AnnouncementStatus,
        created_at: datetime,
        last_modified_at: datetime,
        archived_at: datetime | None = None,
    ) -> None:
        super().__init__(announcement_id, created_at, last_modified_at)
        self._agency_id = agency_id
        self._title = title
        self._description = description
        self._gallery = gallery
        self._itinerary = itinerary
        self._inclusions = inclusions
        self._meeting_point = meeting_point
        self._dates = dates
        self._price_per_person = price_per_person
        self._capacity = capacity
        self._status = status
        self._archived_at = archived_at

    @classmethod
    def create(
        cls,
        *,
        agency_id: Id[Agency],
        title: str | None,
        description: str | None,
        photos: list[str],
        itinerary: list[ItineraryItem],
        included: list[str],
        excluded: list[str],
        meeting_address: str | None,
        meeting_time: time,
        start_date: date,
        end_date: date,
        price_amount: Decimal,
        currency: str | None,
        now: datetime,
    ) -> Result[Announcement, IDomainError]:




        gallery_result = PhotoGallery.create(photos)
        if gallery_result.is_failure:
            return failure(gallery_result.error)

        itinerary_result = Itinerary.create(itinerary)
        if itinerary_result.is_failure:
            return failure(itinerary_result.error)

        inclusions_result = Inclusions.create(included, excluded)
        if inclusions_result.is_failure:
            return failure(inclusions_result.error)

        meeting_result = MeetingPoint.create(meeting_address, meeting_time)
        if meeting_result.is_failure:
            return failure(meeting_result.error)

        dates_result = DateRange.create(start_date, end_date)
        if dates_result.is_failure:
            return failure(dates_result.error)

        price_result = Money.create(price_amount, currency)
        if price_result.is_failure:
            return failure(price_result.error)

        # cross-field rule no single value object can own: a new tour must start in the future
        if dates_result.value.start <= now.date():
            return failure(
                DomainError.validation(
                    "A new announcement must start in the future.",
                    AnnouncementErrorCodes.START_IN_PAST,
                )
            )

        return success(
            cls(
                Id.new(),
                agency_id,
                title,
                description,
                gallery_result.value,
                itinerary_result.value,
                inclusions_result.value,
                meeting_result.value,
                dates_result.value,
                price_result.value,
                AnnouncementStatus.PUBLISHED,
                now,
                now,
            )
        )

    # ---- properties ------------------------------------------------------------------------

    @property
    def agency_id(self) -> Id[Agency]:
        return self._agency_id

    @property
    def title(self) -> str:
        return self._title

    @property
    def description(self) -> str:
        return self._description

    @property
    def gallery(self) -> PhotoGallery:
        return self._gallery

    @property
    def itinerary(self) -> Itinerary:
        return self._itinerary

    @property
    def inclusions(self) -> Inclusions:
        return self._inclusions

    @property
    def meeting_point(self) -> MeetingPoint:
        return self._meeting_point

    @property
    def start_date(self) -> date:
        return self._start_date
    
    @property
    def end_date(self) -> date:
        return self._end_date

    @property
    def price_per_person(self) -> Money:
        return self._price_per_person

    @property
    def capacity(self) -> int:
        return self._capacity


    @property
    def status(self) -> AnnouncementStatus:
        return self._status

    @property
    def archived_at(self) -> datetime | None:
        return self._archived_at

    @property
    def is_published(self) -> bool:
        return self._status is AnnouncementStatus.PUBLISHED