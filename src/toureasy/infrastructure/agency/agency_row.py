import uuid
from datetime import datetime

from sqlalchemy import DateTime, Index, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from toureasy.infrastructure.database import Base


class AgencyRow(Base):
    """Shape of the ``agencies`` table. No business rules: ``AgencyRepository`` maps it to ``Agency``."""

    __tablename__ = "agencies"
    __table_args__ = (Index("ix_agencies_status_created_at_utc", "status", "created_at_utc"),)

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True)
    name: Mapped[str] = mapped_column(String(200))
    contact_email: Mapped[str] = mapped_column(String(254))
    status: Mapped[str] = mapped_column(String(32))
    rejection_reason: Mapped[str | None] = mapped_column(String(500))
    created_at_utc: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    last_modified_at_utc: Mapped[datetime] = mapped_column(DateTime(timezone=True))
