import uuid
from datetime import datetime, timezone
from enum import Enum

from sqlalchemy import DateTime, ForeignKey, String, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class JobStatus(str, Enum):
    PENDING = "pending"
    INGESTING = "ingesting"
    PARSING = "parsing"
    RECONSTRUCTING = "reconstructing"
    SYNTHESIZING = "synthesizing"
    POSTPROCESSING = "postprocessing"
    COMPLETE = "complete"
    FAILED = "failed"


class Job(Base):
    __tablename__ = "jobs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    property_id: Mapped[str] = mapped_column(ForeignKey("properties.id"), index=True)
    status: Mapped[JobStatus] = mapped_column(String(32), default=JobStatus.PENDING)
    current_stage: Mapped[str | None] = mapped_column(String(64), nullable=True)
    progress_pct: Mapped[int] = mapped_column(default=0)
    # Path / CDN URL of the final video
    output_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    # Intermediate parsed room data from Stage 2
    parsed_rooms: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    # Rendered interior image S3 keys from Stage 3
    render_keys: Mapped[list | None] = mapped_column(JSON, nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    celery_task_id: Mapped[str | None] = mapped_column(String(256), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    property: Mapped["Property"] = relationship("Property", back_populates="jobs")  # type: ignore[name-defined]
    assets: Mapped[list["Asset"]] = relationship("Asset", back_populates="job", lazy="selectin")  # type: ignore[name-defined]
