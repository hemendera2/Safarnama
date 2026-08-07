from sqlalchemy import JSON, Float, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import db, generate_uuid


class IntelligenceScore(db.Model):
    __tablename__ = "intelligence_scores"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    place_id: Mapped[str] = mapped_column(
        ForeignKey("places.id"), nullable=False, index=True
    )

    # Dimensions (0.0 to 1.0)
    photography: Mapped[float] = mapped_column(Float, default=0.5)
    adventure: Mapped[float] = mapped_column(Float, default=0.5)
    relaxation: Mapped[float] = mapped_column(Float, default=0.5)
    offbeat: Mapped[float] = mapped_column(Float, default=0.5)
    family_friendly: Mapped[float] = mapped_column(Float, default=0.5)
    couple_friendly: Mapped[float] = mapped_column(Float, default=0.5)
    road_trip_value: Mapped[float] = mapped_column(Float, default=0.5)

    # Contextual Weights
    monsoon_value: Mapped[float] = mapped_column(Float, default=0.5)
    winter_value: Mapped[float] = mapped_column(Float, default=0.5)
    summer_value: Mapped[float] = mapped_column(Float, default=0.5)

    place = relationship("Place", back_populates="intelligence")


class RecommendationBenchmark(db.Model):
    __tablename__ = "recommendation_benchmarks"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    query_text: Mapped[str] = mapped_column(String(500), nullable=False)
    expected_place_ids: Mapped[dict] = mapped_column(
        JSON, nullable=False
    )  # List of IDs that SHOULD appear
    category: Mapped[str] = mapped_column(String(100))  # e.g., "Monsoon", "Budget"
