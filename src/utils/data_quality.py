from pydantic import BaseModel, Field, field_validator
from typing import List, Optional, Dict
import uuid

class LocationValidationSchema(BaseModel):
    name: str = Field(..., min_length=2)
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    crowd_factor: int = Field(..., ge=1, le=5)
    category_name: str
    state_name: str
    city_name: str
    
    @field_validator('name')
    @classmethod
    def name_must_not_be_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError('Name cannot be empty')
        return v

def validate_db_consistency(session):
    from src.models.place import Place
    places = session.query(Place).all()
    errors = []
    
    for p in places:
        try:
            LocationValidationSchema(
                name=p.name,
                latitude=p.latitude,
                longitude=p.longitude,
                crowd_factor=p.crowd_factor,
                category_name=p.category.name if p.category else "",
                state_name=p.state.name if p.state else "",
                city_name=p.city.name if p.city else ""
            )
        except Exception as e:
            errors.append({"place_id": p.id, "error": str(e)})
            
    return errors
