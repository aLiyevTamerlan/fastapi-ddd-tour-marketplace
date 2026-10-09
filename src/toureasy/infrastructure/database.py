from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Base for all ``*Row`` models. Rows describe tables only; they are never domain entities."""


def create_engine(database_url: str, echo: bool = False) -> AsyncEngine:
    return create_async_engine(database_url, echo=echo)


def create_session_factory(engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
    # expire_on_commit=False: reading attributes after commit would otherwise trigger lazy IO (MissingGreenlet).
    return async_sessionmaker(engine, expire_on_commit=False)
