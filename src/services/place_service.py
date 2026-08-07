from src.repositories.place_repository import place_repository

class PlaceService:
    def search(self, filters: dict, page: int, per_page: int):
        return place_repository.search_places(filters, page, per_page)

    def get_discovery(self):
        return place_repository.get_discovery_collections()

    def get_by_id(self, id: str):
        return place_repository.get_by_id(id)

place_service = PlaceService()
