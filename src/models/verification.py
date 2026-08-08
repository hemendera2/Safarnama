from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import db, generate_uuid


class VerificationLog(db.Model):
    __tablename__ = "verification_logs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    place_id: Mapped[str] = mapped_column(
        ForeignKey("places.id"), nullable=False, index=True
    )

    source: Mapped[str] = mapped_column(
        String(200), nullable=False
    )  # e.g., "OpenStreetMap"
    summary: Mapped[str] = mapped_column(
        String(500), nullable=False
    )  # e.g., "Trail Difficulty Updated"

    verified_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())

    place = relationship("Place", back_populates="verification_history")
