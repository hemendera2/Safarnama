from datetime import datetime

from sqlalchemy import (
    JSON,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Table,
    Text,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import db, generate_uuid

# Association Tables
place_tags = Table(
    "place_tags",
    db.Model.metadata,
    db.Column("place_id", ForeignKey("places.id"), primary_key=True),
    db.Column("tag_id", ForeignKey("tags.id"), primary_key=True),
)

place_activities = Table(
    "place_activities",
    db.Model.metadata,
    db.Column("place_id", ForeignKey("places.id"), primary_key=True),
    db.Column("activity_id", ForeignKey("activities.id"), primary_key=True),
)


class Category(db.Model):
    __tablename__ = "categories"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    places = relationship("Place", back_populates="category")


class SubCategory(db.Model):
    __tablename__ = "subcategories"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    category_id: Mapped[str] = mapped_column(
        ForeignKey("categories.id"), nullable=False
    )
    places = relationship("Place", back_populates="subcategory")


class Tag(db.Model):
    __tablename__ = "tags"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)


class Activity(db.Model):
    __tablename__ = "activities"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)


class Place(db.Model):
    __tablename__ = "places"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    name: Mapped[str] = mapped_column(String(200), nullable=False, index=True)

    # Hierarchy
    state_id: Mapped[str] = mapped_column(
        ForeignKey("states.id"), nullable=False, index=True
    )
    city_id: Mapped[str] = mapped_column(
        ForeignKey("cities.id"), nullable=False, index=True
    )
    village_id: Mapped[str] = mapped_column(
        ForeignKey("villages.id"), nullable=True, index=True
    )

    # Classification
    category_id: Mapped[str] = mapped_column(
        ForeignKey("categories.id"), nullable=False, index=True
    )
    subcategory_id: Mapped[str] = mapped_column(
        ForeignKey("subcategories.id"), nullable=True, index=True
    )

    # Geospatial (Indexing coordinates for bounding box optimizations)
    latitude: Mapped[float] = mapped_column(Float, nullable=False, index=True)
    longitude: Mapped[float] = mapped_column(Float, nullable=False, index=True)
    altitude: Mapped[int] = mapped_column(Integer, nullable=True)

    # Extended Metadata
    description: Mapped[str] = mapped_column(Text, nullable=False)
    history: Mapped[str] = mapped_column(Text, nullable=True)
    culture: Mapped[str] = mapped_column(Text, nullable=True)
    interesting_facts: Mapped[str] = mapped_column(Text, nullable=True)

    # Travel Info
    how_to_reach: Mapped[str] = mapped_column(Text, nullable=True)
    best_time_to_visit: Mapped[str] = mapped_column(
        String(200)
    )  # e.g. "Monsoon", "Oct-Mar"
    worst_time_to_visit: Mapped[str] = mapped_column(String(200), nullable=True)
    budget_estimate: Mapped[str] = mapped_column(
        String(100), nullable=True
    )  # e.g. "< ₹2000", "Luxury"

    # Ratings & Factors
    crowd_factor: Mapped[int] = mapped_column(Integer, default=1)  # 1-5
    safety_rating: Mapped[int] = mapped_column(Integer, default=5)  # 1-5
    difficulty_level: Mapped[str] = mapped_column(
        String(50), nullable=True
    )  # Easy, Moderate, Hard

    # Facilities (JSON for flexibility)
    facilities: Mapped[dict] = mapped_column(JSON, default=dict)
    # { "parking": true, "restrooms": true, "atm": false, "network": "Poor" }

    # Status & Trust
    is_published: Mapped[bool] = mapped_column(db.Boolean, default=False)
    confidence_score: Mapped[float] = mapped_column(Float, default=1.0)  # 0.0 to 1.0
    source_attribution: Mapped[str] = mapped_column(
        String(500), nullable=True
    )  # Origin of data
    last_verified_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())

    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=func.now(), onupdate=func.now()
    )

    # Relationships
    state = relationship("State", back_populates="places")
    city = relationship("City", back_populates="places")
    village = relationship("Village", back_populates="places")
    category = relationship("Category", back_populates="places")
    subcategory = relationship("SubCategory", back_populates="places")
    tags = relationship("Tag", secondary=place_tags)
    activities = relationship("Activity", secondary=place_activities)
    images = relationship("PlaceImage", back_populates="place")
    reviews = relationship("Review", back_populates="place")

    # Knowledge Graph Edges
    outgoing_relationships = relationship(
        "NodeRelationship",
        foreign_keys="NodeRelationship.source_id",
        back_populates="source",
    )
    incoming_relationships = relationship(
        "NodeRelationship",
        foreign_keys="NodeRelationship.target_id",
        back_populates="target",
    )

    # Trust & History
    intelligence = relationship(
        "IntelligenceScore", back_populates="place", uselist=False
    )
    verification_history = relationship(
        "VerificationLog",
        back_populates="place",
        order_by="VerificationLog.verified_at.desc()",
    )

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "state": self.state.name if self.state else None,
            "city": self.city.name if self.city else None,
            "category": self.category.name if self.category else None,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "altitude": self.altitude,
            "description": self.description,
            "best_time": self.best_time_to_visit,
            "crowd_factor": self.crowd_factor,
            "safety_rating": self.safety_rating,
            "tags": [tag.name for tag in self.tags],
            "activities": [act.name for act in self.activities],
            "facilities": self.facilities,
            "budget": self.budget_estimate,
            "trust_signal": {
                "confidence": self.confidence_score,
                "source": self.source_attribution,
                "verified_at": (
                    self.last_verified_at.isoformat() if self.last_verified_at else None
                ),
                "timeline": [
                    {
                        "source": log.source,
                        "summary": log.summary,
                        "date": log.verified_at.strftime("%B %Y"),
                    }
                    for log in self.verification_history
                ],
            },
            "hero_image": next((img.url for img in self.images if img.is_hero), None),
            "relationships": [
                {
                    "target_id": rel.target_id,
                    "target_name": rel.target.name,
                    "type": rel.rel_type.value,
                    "weight": rel.weight,
                }
                for rel in self.outgoing_relationships
            ],
        }


class PlaceImage(db.Model):
    __tablename__ = "place_images"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    place_id: Mapped[str] = mapped_column(ForeignKey("places.id"), nullable=False)
    url: Mapped[str] = mapped_column(String(500), nullable=False)
    is_hero: Mapped[bool] = mapped_column(db.Boolean, default=False)
    image_type: Mapped[str] = mapped_column(
        String(50), default="gallery"
    )  # hero, gallery, drone, 360
    place = relationship("Place", back_populates="images")


class Review(db.Model):
    __tablename__ = "reviews"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    place_id: Mapped[str] = mapped_column(ForeignKey("places.id"), nullable=False)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), nullable=False)
    rating: Mapped[int] = mapped_column(Integer, nullable=False)  # 1-5
    comment: Mapped[str] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())

    place = relationship("Place", back_populates="reviews")
    user = relationship("User", back_populates="reviews")
