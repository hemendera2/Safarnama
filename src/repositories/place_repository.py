from .base_repository import BaseRepository
from src.models.place import Place, Tag, Activity, Category
from sqlalchemy.orm import joinedload
from sqlalchemy import func, and_, or_
from src.models import db
import math

class PlaceRepository(BaseRepository[Place]):
    def __init__(self):
        super().__init__(Place)

    def search_places(self, filters: dict, page: int = 1, per_page: int = 20):
        query = db.session.query(Place).options(
            joinedload(Place.state),
            joinedload(Place.city),
            joinedload(Place.category),
            joinedload(Place.tags)
        )

        # Name search
        if filters.get("q"):
            query = query.filter(Place.name.ilike(f'%{filters["q"]}%'))

        # Category filter
        if filters.get("category"):
            query = query.join(Category).filter(Category.name == filters["category"])

        # Tag filters
        if filters.get("tags"):
            query = query.join(Place.tags).filter(Tag.name.in_(filters["tags"]))

        # Crowd factor
        if filters.get("max_crowd"):
            query = query.filter(Place.crowd_factor <= int(filters["max_crowd"]))

        # Geospatial: Radius Search (Haversine formula for SQLite fallback)
        # In PostGIS, we would use ST_DWithin
        lat = filters.get("lat")
        lon = filters.get("lon")
        radius = filters.get("radius") # in km

        if lat and lon and radius:
            # Simple bounding box first for optimization
            lat, lon, radius = float(lat), float(lon), float(radius)
            deg_lat = radius / 111.0
            deg_lon = radius / (111.0 * math.cos(math.radians(lat)))
            
            query = query.filter(
                and_(
                    Place.latitude >= lat - deg_lat,
                    Place.latitude <= lat + deg_lat,
                    Place.longitude >= lon - deg_lon,
                    Place.longitude <= lon + deg_lon
                )
            )

        # Pagination
        return query.paginate(page=page, per_page=per_page, error_out=False)

    def get_discovery_collections(self):
        # Automated collections based on Graph weights and Tags
        collections = {
            "Hidden Gems": self.get_by_tag("Hidden Gem", limit=5),
            "Monsoon Special": self.get_by_tag("Monsoon Spot", limit=5),
            "Sunset Points": self.get_by_tag("Sunset Point", limit=5),
            "Recommended Routes": self.get_places_with_relationships(limit=5)
        }
        return collections

    def get_places_with_relationships(self, limit=5):
        # Discover places that are part of a connected network/route
        return db.session.query(Place).join(Place.outgoing_relationships).limit(limit).all()

    def get_by_tag(self, tag_name, limit=5):
        return db.session.query(Place).join(Place.tags).filter(Tag.name == tag_name).limit(limit).all()

place_repository = PlaceRepository()
