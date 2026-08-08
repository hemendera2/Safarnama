from sqlalchemy import Boolean, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import db, generate_uuid


class Country(db.Model):
    __tablename__ = "countries"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    code: Mapped[str] = mapped_column(String(5), unique=True, nullable=False)

    states = relationship("State", back_populates="country")


class State(db.Model):
    __tablename__ = "states"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    country_id: Mapped[str] = mapped_column(ForeignKey("countries.id"), nullable=False)
    region: Mapped[str] = mapped_column(String(50))  # North, South, etc.

    country = relationship("Country", back_populates="states")
    districts = relationship("District", back_populates="state")
    places = relationship("Place", back_populates="state")


class District(db.Model):
    __tablename__ = "districts"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    state_id: Mapped[str] = mapped_column(ForeignKey("states.id"), nullable=False)

    state = relationship("State", back_populates="districts")
    cities = relationship("City", back_populates="district")


class City(db.Model):
    __tablename__ = "cities"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    district_id: Mapped[str] = mapped_column(ForeignKey("districts.id"), nullable=False)
    is_offbeat_hub: Mapped[bool] = mapped_column(Boolean, default=False)

    district = relationship("District", back_populates="cities")
    villages = relationship("Village", back_populates="city")
    places = relationship("Place", back_populates="city")


class Village(db.Model):
    __tablename__ = "villages"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    city_id: Mapped[str] = mapped_column(ForeignKey("cities.id"), nullable=False)

    city = relationship("City", back_populates="villages")
    places = relationship("Place", back_populates="village")
