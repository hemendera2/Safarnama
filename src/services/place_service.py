from src.repositories.place_repository import place_repository
from src.services.recommendation_engine import recommendation_engine

class PlaceService:
    def search(self, filters: dict, page: int, per_page: int):
        pagination = place_repository.search_places(filters, page, per_page)
        
        # Apply Recommendation Engine Ranking to results
        context = {
            "season": filters.get("season", "monsoon"),
            "interest": filters.get("interest"),
            "vibe": filters.get("vibe")
        }
        
        ranked_items = recommendation_engine.rank_places(pagination.items, context)
        # Re-attach to pagination object or return directly
        pagination.ranked_items = ranked_items
        return pagination

    def get_discovery(self):
        return place_repository.get_discovery_collections()

    def get_by_id(self, id: str):
        return place_repository.get_by_id(id)

place_service = PlaceService()
