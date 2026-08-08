from .base import db, generate_uuid
from sqlalchemy import String, ForeignKey, DateTime, func, Integer, Date, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime

class Itinerary(db.Model):
    __tablename__ = "itineraries"
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    start_date: Mapped[datetime] = mapped_column(Date, nullable=True)
    end_date: Mapped[datetime] = mapped_column(Date, nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())

    user = relationship("User", backref="itineraries")
    stops = relationship("ItineraryStop", back_populates="itinerary", order_by="ItineraryStop.day_number, ItineraryStop.sequence", cascade="all, delete-orphan")

class ItineraryStop(db.Model):
    __tablename__ = "itinerary_stops"
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    itinerary_id: Mapped[str] = mapped_column(ForeignKey("itineraries.id"), nullable=False, index=True)
    place_id: Mapped[str] = mapped_column(ForeignKey("places.id"), nullable=False, index=True)
    
    day_number: Mapped[int] = mapped_column(Integer, default=1)
    sequence: Mapped[int] = mapped_column(Integer, default=1)
    notes: Mapped[str] = mapped_column(Text, nullable=True)
    
    itinerary = relationship("Itinerary", back_populates="stops")
    place = relationship("Place")
