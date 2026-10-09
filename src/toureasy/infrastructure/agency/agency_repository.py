from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from toureasy.application.agency.abstractions.agency_repository import IAgencyRepository
from toureasy.common.identity import Id
from toureasy.domain.agency.agency import Agency
from toureasy.domain.agency.enums import AgencyStatus
from toureasy.infrastructure.agency.agency_row import AgencyRow


class AgencyRepository(IAgencyRepository):
    """The only place that writes agencies to the database. Commits after each successful write."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def add(self, agency: Agency) -> None:
        self._session.add(AgencyRow(**_to_values(agency)))
        await self._session.commit()

    async def update(self, agency: Agency) -> None:
        values = _to_values(agency)
        agency_id = values.pop("id")
        await self._session.execute(update(AgencyRow).where(AgencyRow.id == agency_id).values(**values))
        await self._session.commit()

    async def get(self, agency_id: Id[Agency]) -> Agency | None:
        row = await self._session.get(AgencyRow, agency_id.value)
        return _to_entity(row) if row is not None else None

    async def list_by_status(self, status: AgencyStatus | None) -> list[Agency]:
        query = select(AgencyRow).order_by(AgencyRow.created_at_utc)
        if status is not None:
            query = query.where(AgencyRow.status == status.value)
        rows = (await self._session.scalars(query)).all()
        return [_to_entity(row) for row in rows]


def _to_values(agency: Agency) -> dict[str, Any]:
    return {
        "id": agency.id.value,
        "name": agency.name.value,
        "contact_email": agency.contact_email.value,
        "status": agency.status.value,
        "rejection_reason": agency.rejection_reason,
        "created_at_utc": agency.created_at_utc,
        "last_modified_at_utc": agency.last_modified_at_utc,
    }


def _to_entity(row: AgencyRow) -> Agency:
    # Always rehydrate, never call the constructor: storage data is trusted, not re-validated.
    return Agency.rehydrate(
        agency_id=row.id,
        name=row.name,
        contact_email=row.contact_email,
        status=row.status,
        rejection_reason=row.rejection_reason,
        created_at=_as_utc(row.created_at_utc),
        last_modified_at=_as_utc(row.last_modified_at_utc),
    )


def _as_utc(value: datetime) -> datetime:
    """Postgres ``timestamptz`` returns aware values; drivers without time zones (SQLite) return naive UTC."""
    return value if value.tzinfo is not None else value.replace(tzinfo=UTC)
