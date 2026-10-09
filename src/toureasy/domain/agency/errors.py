from typing import Final


class AgencyErrorCodes:
    # Agency
    INVALID_AGENCY: Final = "invalid_agency"
    INVALID_AGENCY_NAME: Final = "invalid_agency_name"
    INVALID_CONTACT_EMAIL: Final = "invalid_contact_email"
    INVALID_AGENCY_STATUS: Final = "invalid_agency_status"
    INVALID_REJECTION_REASON: Final = "invalid_rejection_reason"
    AGENCY_NOT_FOUND: Final = "agency_not_found"
    AGENCY_NOT_ACTIVE: Final = "agency_not_active"
    AGENCY_NOT_PENDING_VERIFICATION: Final = "agency_not_pending_verification"
    AGENCY_NOT_SUSPENDED: Final = "agency_not_suspended"
    AGENCY_SUSPENDED: Final = "agency_suspended"
    AGENCY_ALREADY_SUSPENDED: Final = "agency_already_suspended"
    AGENCY_ALREADY_ACTIVE: Final = "agency_already_active"

    # Announcement
    INVALID_ANNOUNCEMENT: Final = "invalid_announcement"
    INVALID_ANNOUNCEMENT_TITLE: Final = "invalid_announcement_title"
    INVALID_DATE_RANGE: Final = "invalid_date_range"
    INVALID_PRICE: Final = "invalid_price"
    INVALID_CURRENCY: Final = "invalid_currency"
    INVALID_CAPACITY: Final = "invalid_capacity"


class AnnouncementErrorCodes:
    """Stable, machine-readable codes for Announcement domain failures.

    The string is what the API returns to the client (error `detail.code`);
    `base_controller` maps the DomainError's *type* (validation/conflict/...) to
    the HTTP status, never these codes. Keep the strings stable — the frontend
    switches on them.
    """

    # --- title ---
    TITLE_EMPTY:             Final[str] = "announcement.title_empty"
    TITLE_TOO_LONG:          Final[str] = "announcement.title_too_long"

    # --- description ---
    DESCRIPTION_TOO_SHORT:   Final[str] = "announcement.description_too_short"
    DESCRIPTION_TOO_LONG:    Final[str] = "announcement.description_too_long"

    # --- photo gallery ---
    GALLERY_EMPTY:           Final[str] = "announcement.gallery_empty"
    GALLERY_TOO_LARGE:       Final[str] = "announcement.gallery_too_large"

    # --- itinerary ---
    ITINERARY_EMPTY:         Final[str] = "announcement.itinerary_empty"

    # --- meeting point ---
    MEETING_POINT_EMPTY:     Final[str] = "announcement.meeting_point_empty"

    # --- dates ---
    DATE_RANGE_INVALID:      Final[str] = "announcement.date_range_invalid"
    START_IN_PAST:           Final[str] = "announcement.start_in_past"

    # --- price / money ---
    PRICE_INVALID:           Final[str] = "announcement.price_invalid"
    CURRENCY_INVALID:        Final[str] = "announcement.currency_invalid"

    # --- capacity ---
    CAPACITY_INVALID:        Final[str] = "announcement.capacity_invalid"

    # --- deposit policy (T-11) ---
    DEPOSIT_INVALID:         Final[str] = "announcement.deposit_invalid"

    # --- cancellation policy ---
    CANCELLATION_INVALID:    Final[str] = "announcement.cancellation_invalid"

    # --- booking / price breakdown ---
    TRAVELERS_INVALID:       Final[str] = "announcement.travelers_invalid"

    # --- lifecycle / cross-entity ---
    AGENCY_NOT_FOUND:        Final[str] = "announcement.agency_not_found"
    ALREADY_ARCHIVED:        Final[str] = "announcement.already_archived"
    HAS_ACTIVE_RESERVATIONS: Final[str] = "announcement.has_active_reservations"


class MoneyErrorCodes:
    AMOUNT_REQUIRED:          Final[str] = "money.amount_required"
    AMOUNT_INVALID:           Final[str] = "money.amount_invalid"
    AMOUNT_NEGATIVE:          Final[str] = "money.amount_negative"
    AMOUNT_TOO_MANY_DECIMALS: Final[str] = "money.amount_too_many_decimals"
    CURRENCY_INVALID:         Final[str] = "money.currency_invalid"