import enum

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from werkzeug.security import check_password_hash, generate_password_hash

from .base import db, generate_uuid


class UserRole(enum.Enum):
    TRAVELER = "traveler"
    CONTRIBUTOR = "contributor"
    MODERATOR = "moderator"
    ADMIN = "admin"


class User(db.Model):
    __tablename__ = "users"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    email: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(256), nullable=False)
    full_name: Mapped[str] = mapped_column(String(100), nullable=True)
    role: Mapped[UserRole] = mapped_column(Enum(UserRole), default=UserRole.TRAVELER)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[DateTime] = mapped_column(DateTime, default=func.now())

    reviews = relationship("Review", back_populates="user")
    favorites = relationship("Place", secondary="user_favorites")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


# Association table for User Favorites
user_favorites = db.Table(
    "user_favorites",
    db.Model.metadata,
    db.Column("user_id", ForeignKey("users.id"), primary_key=True),
    db.Column("place_id", ForeignKey("places.id"), primary_key=True),
)
