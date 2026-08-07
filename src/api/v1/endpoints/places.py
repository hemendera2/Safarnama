from flask import Blueprint, jsonify, request

from src.services.place_service import place_service

router = Blueprint("places", __name__)


@router.route("/", methods=["GET"])
def get_places():
    filters = {
        "q": request.args.get("q"),
        "category": request.args.get("category"),
        "tags": request.args.getlist("tags"),
        "lat": request.args.get("lat"),
        "lon": request.args.get("lon"),
        "radius": request.args.get("radius"),
        "max_crowd": request.args.get("max_crowd"),
        "season": request.args.get("season"),
        "interest": request.args.get("interest"),
        "vibe": request.args.get("vibe"),
    }
    page = int(request.args.get("page", 1))
    per_page = int(request.args.get("per_page", 20))

    pagination = place_service.search(filters, page, per_page)

    return jsonify(
        {
            "items": pagination.ranked_items,
            "total": pagination.total,
            "page": pagination.page,
            "pages": pagination.pages,
            "has_next": pagination.has_next,
            "has_prev": pagination.has_prev,
        }
    )


@router.route("/discovery", methods=["GET"])
def discovery():
    collections = place_service.get_discovery()
    result = {}
    for name, places in collections.items():
        result[name] = [p.to_dict() for p in places]
    return jsonify(result)


@router.route("/<id>", methods=["GET"])
def get_place(id):
    place = place_service.get_by_id(id)
    if not place:
        return jsonify({"error": "Place not found"}), 404
    return jsonify(place.to_dict())
