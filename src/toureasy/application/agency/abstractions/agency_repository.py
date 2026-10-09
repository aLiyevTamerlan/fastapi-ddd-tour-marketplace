from __future__ import annotations

from abc import ABC, abstractmethod

from toureasy.common.identity import Id
from toureasy.domain.agency.agency import Agency
from toureasy.domain.agency.enums import AgencyStatus


class IAgencyRepository(ABC):
    """Port for agency storage. Lives in the application layer because its methods are ``async``;
    the implementation (``AgencyRepository``) lives in infrastructure."""

    @abstractmethod
    async def add(self, agency: Agency) -> None: ...

    @abstractmethod
    async def update(self, agency: Agency) -> None: ...

    @abstractmethod
    async def get(self, agency_id: Id[Agency]) -> Agency | None: ...

    @abstractmethod
    async def list_by_status(self, status: AgencyStatus | None) -> list[Agency]:
        """Oldest first, so the verification queue is handled in arrival order. ``None`` lists all."""
