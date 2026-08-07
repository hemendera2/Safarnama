from .base import db, generate_uuid
from sqlalchemy import String, ForeignKey, JSON, DateTime, func, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime

class UserEvent(db.Model):
    __tablename__ = "user_events"
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), nullable=True) # Anonymous if null
    event_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True) # search, click, bookmark, view_trust
    
    # Context data (e.g., query string, place_id, recommendation_reason)
    payload: Mapped[dict] = mapped_column(JSON, nullable=True)
    
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=func.now())

class Bookmark(db.Model):
    __tablename__ = "bookmarks"
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    place_id: Mapped[str] = mapped_column(ForeignKey("places.id"), nullable=False, index=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    
    user = relationship("User", backref="user_bookmarks")
    place = relationship("Place", backref="place_bookmarks")
