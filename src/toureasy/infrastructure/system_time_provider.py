from datetime import UTC, datetime


class SystemTimeProvider:
    """``TimeProvider`` backed by the system clock, always in UTC."""

    def now(self) -> datetime:
        return datetime.now(UTC)
