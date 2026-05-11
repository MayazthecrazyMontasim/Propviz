import uuid
from datetime import datetime, timezone
from enum import Enum

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class AssetType(str, Enum):
    FLOOR_PLAN = "floor_plan"
    PHOTO = "photo"
    BROCHURE = "brochure"
    RENDER = "render"       # AI-generated interior image
    NARRATION = "narration" # TTS audio
    VIDEO_RAW = "video_raw"
    VIDEO_FINAL = "video_final"


class Asset(Base):
    __tablename__ = "assets"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    job_id: Mapped[str] = mapped_column(ForeignKey("jobs.id"), index=True)
    asset_type: Mapped[AssetType] = mapped_column(String(32))
    original_filename: Mapped[str] = mapped_column(String(256))
    s3_key: Mapped[str] = mapped_column(Text)
    mime_type: Mapped[str] = mapped_column(String(128))
    size_bytes: Mapped[int | None] = mapped_column(Integer, nullable=True)
    cdn_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    job: Mapped["Job"] = relationship("Job", back_populates="assets")  # type: ignore[name-defined]
