import uuid
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import DateTime, String, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Property(Base):
    __tablename__ = "properties"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name: Mapped[str] = mapped_column(String(256))
    developer: Mapped[str | None] = mapped_column(String(256), nullable=True)
    location: Mapped[str | None] = mapped_column(Text, nullable=True)
    unit_type: Mapped[str | None] = mapped_column(String(64), nullable=True)
    area_sqft: Mapped[int | None] = mapped_column(nullable=True)
    price_range: Mapped[str | None] = mapped_column(String(128), nullable=True)
    # Structured data: rooms, amenities, landmarks, specs extracted from brochure
    extra_data: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    jobs: Mapped[list["Job"]] = relationship("Job", back_populates="property", lazy="selectin")  # type: ignore[name-defined]
