from __future__ import annotations

from fastapi import APIRouter, Response, status

from toureasy.api.agency.schemas import RegisterAgencyRequest, RejectAgencyRequest, UpdateAgencyRequest
from toureasy.api.dependencies import AgencyServiceDep
from toureasy.api.errors import unwrap
from toureasy.application.agency.dtos import AgencyDto
from toureasy.common.identity import Id
from toureasy.domain.agency.agency import Agency

# Routers only parse input, call the service and turn the Result into HTTP. No business conditions here.

router = APIRouter(prefix="/api/v1/agencies", tags=["agencies"])
admin_router = APIRouter(prefix="/api/v1/admin/agencies", tags=["admin: agencies"])


# ---- agency dashboard ----------------------------------------------------------------------


@router.post("", status_code=status.HTTP_201_CREATED)
async def register_agency(body: RegisterAgencyRequest, response: Response, service: AgencyServiceDep) -> AgencyDto:
    agency = unwrap(await service.register(body.name, body.contact_email))
    response.headers["Location"] = f"{router.prefix}/{agency.id}"
    return agency


@router.get("/{agency_id}")
async def get_agency(agency_id: str, service: AgencyServiceDep) -> AgencyDto:
    parsed = unwrap(Id[Agency].parse(agency_id))
    return unwrap(await service.get(parsed))


@router.patch("/{agency_id}")
async def update_agency(agency_id: str, body: UpdateAgencyRequest, service: AgencyServiceDep) -> AgencyDto:
    parsed = unwrap(Id[Agency].parse(agency_id))
    return unwrap(await service.update_profile(parsed, body.name, body.contact_email))


# ---- admin ---------------------------------------------------------------------------------


@admin_router.get("")
async def list_agencies(service: AgencyServiceDep, status: str | None = None) -> list[AgencyDto]:
    """Verification queue: ``?status=PendingVerification``."""
    return unwrap(await service.list_by_status(status))


@admin_router.post("/{agency_id}/verify")
async def verify_agency(agency_id: str, service: AgencyServiceDep) -> AgencyDto:
    parsed = unwrap(Id[Agency].parse(agency_id))
    return unwrap(await service.verify(parsed))


@admin_router.post("/{agency_id}/reject")
async def reject_agency(agency_id: str, body: RejectAgencyRequest, service: AgencyServiceDep) -> AgencyDto:
    parsed = unwrap(Id[Agency].parse(agency_id))
    return unwrap(await service.reject(parsed, body.reason))


@admin_router.post("/{agency_id}/suspend")
async def suspend_agency(agency_id: str, service: AgencyServiceDep) -> AgencyDto:
    parsed = unwrap(Id[Agency].parse(agency_id))
    return unwrap(await service.suspend(parsed))


@admin_router.post("/{agency_id}/reactivate")
async def reactivate_agency(agency_id: str, service: AgencyServiceDep) -> AgencyDto:
    parsed = unwrap(Id[Agency].parse(agency_id))
    return unwrap(await service.reactivate(parsed))
