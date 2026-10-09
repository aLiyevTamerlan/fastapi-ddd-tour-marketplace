from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from toureasy.api.agency.agency_router import admin_router as admin_agency_router
from toureasy.api.agency.agency_router import router as agency_router
from toureasy.infrastructure.config import Settings
from toureasy.infrastructure.database import create_engine, create_session_factory


def create_app(settings: Settings | None = None) -> FastAPI:
    """Composition root: wires the layers together. Run with ``uv run uvicorn toureasy.main:app``."""
    app_settings = settings or Settings()

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[None]:
        engine = create_engine(app_settings.database_url, echo=app_settings.database_echo)
        app.state.session_factory = create_session_factory(engine)
        yield
        await engine.dispose()

    app = FastAPI(title="TourEasy API", lifespan=lifespan)
    app.include_router(agency_router)
    app.include_router(admin_agency_router)
    return app


app = create_app()
