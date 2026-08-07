from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from src.models import db, Itinerary, ItineraryStop, Place

router = Blueprint("itinerary", __name__)

@router.route("/", methods=["POST"])
@jwt_required()
def create_itinerary():
    user_id = get_jwt_identity()
    data = request.get_json()
    
    itinerary = Itinerary(
        user_id=user_id,
        title=data["title"],
        description=data.get("description")
    )
    db.session.add(itinerary)
    db.session.commit()
    
    return jsonify({"id": itinerary.id, "title": itinerary.title}), 201

@router.route("/", methods=["GET"])
@jwt_required()
def get_itineraries():
    user_id = get_jwt_identity()
    itineraries = Itinerary.query.filter_by(user_id=user_id).all()
    return jsonify([{
        "id": it.id,
        "title": it.title,
        "created_at": it.created_at.isoformat()
    } for it in itineraries])

@router.route("/<itinerary_id>", methods=["GET"])
@jwt_required()
def get_itinerary(itinerary_id):
    user_id = get_jwt_identity()
    itinerary = Itinerary.query.filter_by(id=itinerary_id, user_id=user_id).first()
    if not itinerary:
        return jsonify({"error": "Not found"}), 404
        
    return jsonify({
        "id": itinerary.id,
        "title": itinerary.title,
        "description": itinerary.description,
        "stops": [{
            "id": stop.id,
            "place_id": stop.place_id,
            "place_name": stop.place.name,
            "day_number": stop.day_number,
            "sequence": stop.sequence,
            "notes": stop.notes
        } for stop in itinerary.stops]
    })

@router.route("/<itinerary_id>/stops", methods=["POST"])
@jwt_required()
def add_stop(itinerary_id):
    user_id = get_jwt_identity()
    itinerary = Itinerary.query.filter_by(id=itinerary_id, user_id=user_id).first()
    if not itinerary:
        return jsonify({"error": "Not found"}), 404
        
    data = request.get_json()
    stop = ItineraryStop(
        itinerary_id=itinerary_id,
        place_id=data["place_id"],
        day_number=data.get("day_number", 1),
        sequence=len(itinerary.stops) + 1,
        notes=data.get("notes")
    )
    db.session.add(stop)
    db.session.commit()
    
    return jsonify({"id": stop.id}), 201

@router.route("/<itinerary_id>/stops/reorder", methods=["POST"])
@jwt_required()
def reorder_stops(itinerary_id):
    user_id = get_jwt_identity()
    itinerary = Itinerary.query.filter_by(id=itinerary_id, user_id=user_id).first()
    if not itinerary:
        return jsonify({"error": "Not found"}), 404
        
    data = request.get_json() # List of stop IDs in order
    for idx, stop_id in enumerate(data["stop_ids"]):
        stop = ItineraryStop.query.filter_by(id=stop_id, itinerary_id=itinerary_id).first()
        if stop:
            stop.sequence = idx + 1
            
    db.session.commit()
    return jsonify({"message": "Reordered"}), 200

@router.route("/<itinerary_id>", methods=["DELETE"])
@jwt_required()
def delete_itinerary(itinerary_id):
    user_id = get_jwt_identity()
    itinerary = Itinerary.query.filter_by(id=itinerary_id, user_id=user_id).first()
    if not itinerary:
        return jsonify({"error": "Not found"}), 404
        
    db.session.delete(itinerary)
    db.session.commit()
    return jsonify({"message": "Deleted"}), 200

@router.route("/<itinerary_id>/stops/<stop_id>", methods=["DELETE"])
@jwt_required()
def remove_stop(itinerary_id, stop_id):
    user_id = get_jwt_identity()
    itinerary = Itinerary.query.filter_by(id=itinerary_id, user_id=user_id).first()
    if not itinerary:
        return jsonify({"error": "Itinerary not found"}), 404
        
    stop = ItineraryStop.query.filter_by(id=stop_id, itinerary_id=itinerary_id).first()
    if not stop:
        return jsonify({"error": "Stop not found"}), 404
        
    db.session.delete(stop)
    db.session.commit()
    return jsonify({"message": "Stop removed"}), 200
