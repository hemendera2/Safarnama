from .base import db, generate_uuid
from sqlalchemy import String, ForeignKey, Enum, Float, Table
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum

class RelationshipType(enum.Enum):
    NEAR = "near"
    ALTERNATIVE = "alternative"
    PART_OF = "part_of"
    CONNECTED_ROUTE = "connected_route"
    RECOMMENDED_TOGETHER = "recommended_together"
    SAME_EXPERIENCE = "same_experience"
    PHOTOGRAPHY_SPOT = "photography_spot"

class NodeRelationship(db.Model):
    __tablename__ = "node_relationships"
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    
    # The source and target nodes (Places)
    source_id: Mapped[str] = mapped_column(ForeignKey("places.id"), nullable=False, index=True)
    target_id: Mapped[str] = mapped_column(ForeignKey("places.id"), nullable=False, index=True)
    
    # Relationship metadata
    rel_type: Mapped[RelationshipType] = mapped_column(Enum(RelationshipType), nullable=False)
    weight: Mapped[float] = mapped_column(Float, default=1.0) # Strength of relationship (0.0 to 1.0)
    
    source = relationship("Place", foreign_keys=[source_id], back_populates="outgoing_relationships")
    target = relationship("Place", foreign_keys=[target_id], back_populates="incoming_relationships")
