from __future__ import annotations

from collections.abc import AsyncIterator
from typing import Annotated

from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from toureasy.application.agency.agency_service import AgencyService
from toureasy.infrastructure.agency.agency_repository import AgencyRepository
from toureasy.infrastructure.system_time_provider import SystemTimeProvider


async def get_session(request: Request) -> AsyncIterator[AsyncSession]:
    """One ``AsyncSession`` per request, closed when the request ends."""
    session_factory: async_sessionmaker[AsyncSession] = request.app.state.session_factory
    async with session_factory() as session:
        yield session


def get_agency_service(session: Annotated[AsyncSession, Depends(get_session)]) -> AgencyService:
    return AgencyService(AgencyRepository(session), SystemTimeProvider())


AgencyServiceDep = Annotated[AgencyService, Depends(get_agency_service)]
