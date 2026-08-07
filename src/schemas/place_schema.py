from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from datetime import datetime

class TagSchema(BaseModel):
    id: str
    name: str
    model_config = ConfigDict(from_attributes=True)

class PlaceBase(BaseModel):
    name: str
    latitude: float
    longitude: float
    description: str
    how_to_reach: Optional[str] = None
    crowd_factor: int
    best_time_to_visit: str

class PlaceCreate(PlaceBase):
    state_id: str
    city_id: str
    category_id: str

class PlaceRead(PlaceBase):
    id: str
    state_name: str
    city_name: str
    category_name: str
    tags: List[str] = []
    
    model_config = ConfigDict(from_attributes=True)
