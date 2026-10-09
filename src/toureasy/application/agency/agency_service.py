from __future__ import annotations

from collections.abc import Callable
from datetime import datetime

from toureasy.application.agency.abstractions.agency_repository import IAgencyRepository
from toureasy.application.agency.dtos import AgencyDto
from toureasy.common.errors.domain_error import DomainError, IDomainError
from toureasy.common.identity import Id
from toureasy.common.result import Result, failure, success
from toureasy.common.time_provider import TimeProvider
from toureasy.domain.agency.agency import Agency
from toureasy.domain.agency.enums import AgencyStatus
from toureasy.domain.agency.errors import AgencyErrorCodes


class AgencyService:
    """Use cases for agencies: load, let the entity decide, save. No business rules live here."""

    def __init__(self, agencies: IAgencyRepository, time_provider: TimeProvider) -> None:
        self._agencies = agencies
        self._time = time_provider

    # ---- agency dashboard ------------------------------------------------------------------

    async def register(self, name: str | None, contact_email: str | None) -> Result[AgencyDto, IDomainError]:
        created = Agency.create(name, contact_email, self._time.now())
        if created.is_failure:
            return failure(created.error)
        await self._agencies.add(created.value)
        return success(AgencyDto.from_entity(created.value))

    async def get(self, agency_id: Id[Agency]) -> Result[AgencyDto, IDomainError]:
        loaded = await self._load(agency_id)
        if loaded.is_failure:
            return failure(loaded.error)
        return success(AgencyDto.from_entity(loaded.value))

    async def update_profile(
        self, agency_id: Id[Agency], name: str | None, contact_email: str | None
    ) -> Result[AgencyDto, IDomainError]:
        """Partial update: a field left as ``None`` is not changed."""
        loaded = await self._load(agency_id)
        if loaded.is_failure:
            return failure(loaded.error)
        agency = loaded.value
        now = self._time.now()

        if name is not None:
            renamed = agency.rename(name, now)
            if renamed.is_failure:
                return failure(renamed.error)
        if contact_email is not None:
            changed = agency.change_contact_email(contact_email, now)
            if changed.is_failure:
                return failure(changed.error)

        await self._agencies.update(agency)
        return success(AgencyDto.from_entity(agency))

    # ---- admin -----------------------------------------------------------------------------

    async def list_by_status(self, status: str | None) -> Result[list[AgencyDto], IDomainError]:
        parsed: AgencyStatus | None = None
        if status is not None:
            try:
                parsed = AgencyStatus.from_name(status)
            except ValueError:
                allowed = ", ".join(s.value for s in AgencyStatus)
                return failure(
                    DomainError.bad_request(
                        f"Unknown agency status {status!r}. Allowed: {allowed}.",
                        code=AgencyErrorCodes.INVALID_AGENCY_STATUS,
                    )
                )
        agencies = await self._agencies.list_by_status(parsed)
        return success([AgencyDto.from_entity(a) for a in agencies])

    async def verify(self, agency_id: Id[Agency]) -> Result[AgencyDto, IDomainError]:
        return await self._change(agency_id, lambda agency, now: agency.verify(now))

    async def reject(self, agency_id: Id[Agency], reason: str | None) -> Result[AgencyDto, IDomainError]:
        return await self._change(agency_id, lambda agency, now: agency.reject(reason, now))

    async def suspend(self, agency_id: Id[Agency]) -> Result[AgencyDto, IDomainError]:
        return await self._change(agency_id, lambda agency, now: agency.suspend(now))

    async def reactivate(self, agency_id: Id[Agency]) -> Result[AgencyDto, IDomainError]:
        return await self._change(agency_id, lambda agency, now: agency.reactivate(now))

    # ---- helpers ---------------------------------------------------------------------------

    async def _load(self, agency_id: Id[Agency]) -> Result[Agency, IDomainError]:
        agency = await self._agencies.get(agency_id)
        if agency is None:
            return failure(DomainError.not_found("Agency not found.", code=AgencyErrorCodes.AGENCY_NOT_FOUND))
        return success(agency)

    async def _change(
        self,
        agency_id: Id[Agency],
        action: Callable[[Agency, datetime], Result[None, IDomainError]],
    ) -> Result[AgencyDto, IDomainError]:
        """Load the agency, apply one domain transition, save only if it succeeded."""
        loaded = await self._load(agency_id)
        if loaded.is_failure:
            return failure(loaded.error)
        agency = loaded.value
        changed = action(agency, self._time.now())
        if changed.is_failure:
            return failure(changed.error)
        await self._agencies.update(agency)
        return success(AgencyDto.from_entity(agency))
