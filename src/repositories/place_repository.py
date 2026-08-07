import math

from sqlalchemy import and_, or_
from sqlalchemy.orm import joinedload

from src.models import db
from src.models.place import Category, Place, Tag

from .base_repository import BaseRepository


class PlaceRepository(BaseRepository[Place]):
    def __init__(self):
        super().__init__(Place)

    def search_places(self, filters: dict, page: int = 1, per_page: int = 20):
        query = db.session.query(Place).options(
            joinedload(Place.state),
            joinedload(Place.city),
            joinedload(Place.category),
            joinedload(Place.tags),
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

        # Intelligent Search Improvements
        if filters.get("q"):
            q = filters["q"].strip().lower()
            
            # 1. Check for State/City/District names in query
            # (In production, we'd use a more sophisticated NER or fuzzy match)
            
            # 2. Alias expansion & Experience mapping
            experiences = {
                "waterfall": "Waterfall",
                "falls": "Waterfall",
                "meadow": "Meadow",
                "valley": "Valley",
                "hill": "Hill",
                "trek": "Trek",
                "trail": "Trek",
                "camp": "Camping"
            }
            for key, val in experiences.items():
                if key in q:
                    query = query.filter(
                        or_(
                            Place.subcategory.has(name=val),
                            Place.category.has(name=val),
                            Place.tags.any(name=val)
                        )
                    )
            
            # 3. Vibe matching
            if any(k in q for k in ["quiet", "peaceful", "silent"]):
                query = query.filter(Place.crowd_factor <= 2)
            if any(k in q for k in ["popular", "famous"]):
                query = query.filter(Place.crowd_factor >= 4)
            
            # 4. Trust/Hidden Gem
            if any(k in q for k in ["verified", "trusted"]):
                query = query.filter(Place.confidence_score >= 0.9)
            if any(k in q for k in ["hidden", "offbeat", "secret"]):
                query = query.filter(Place.confidence_score >= 0.8)
                query = query.filter(Place.crowd_factor <= 2)

        # Crowd factor
        if filters.get("max_crowd"):
            query = query.filter(Place.crowd_factor <= int(filters["max_crowd"]))

        # Geospatial: Radius Search (Haversine formula for SQLite fallback)
        # In PostGIS, we would use ST_DWithin
        lat = filters.get("lat")
        lon = filters.get("lon")
        radius = filters.get("radius")  # in km

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
                    Place.longitude <= lon + deg_lon,
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
            "Recommended Routes": self.get_places_with_relationships(limit=5),
        }
        return collections

    def get_places_with_relationships(self, limit=5):
        # Discover places that are part of a connected network/route
        return (
            db.session.query(Place)
            .options(joinedload(Place.state), joinedload(Place.city), joinedload(Place.category))
            .join(Place.outgoing_relationships)
            .limit(limit)
            .all()
        )

    def get_by_tag(self, tag_name, limit=5):
        return (
            db.session.query(Place)
            .options(joinedload(Place.state), joinedload(Place.city), joinedload(Place.category))
            .join(Place.tags)
            .filter(Tag.name == tag_name)
            .limit(limit)
            .all()
        )


place_repository = PlaceRepository()
