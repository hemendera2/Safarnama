from datetime import datetime

from sqlalchemy import JSON, Boolean, DateTime, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import db, generate_uuid


class UserEvent(db.Model):
    __tablename__ = "user_events"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    user_id: Mapped[str] = mapped_column(
        ForeignKey("users.id"), nullable=True
    )  # Anonymous if null
    session_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    event_type: Mapped[str] = mapped_column(
        String(50), nullable=False, index=True
    )  # search, destination_open, trust_interaction, bookmark, no_results
    test_session: Mapped[bool] = mapped_column(Boolean, default=False)

    # Context data (e.g., query string, place_id, trust_type)
    payload: Mapped[dict] = mapped_column(JSON, nullable=True)

    timestamp: Mapped[datetime] = mapped_column(DateTime, default=func.now())


class Bookmark(db.Model):
    __tablename__ = "bookmarks"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    user_id: Mapped[str] = mapped_column(
        ForeignKey("users.id"), nullable=False, index=True
    )
    place_id: Mapped[str] = mapped_column(
        ForeignKey("places.id"), nullable=False, index=True
    )

    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())

    user = relationship("User", backref="user_bookmarks")
    place = relationship("Place", backref="place_bookmarks")
