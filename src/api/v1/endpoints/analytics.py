from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from src.models import db, UserEvent, Bookmark
from src.utils.logger import logger

router = Blueprint("analytics", __name__)

@router.route("/event", methods=["POST"])
def track_event():
    data = request.get_json()
    # Support anonymous events
    user_id = None
    try:
        # Check if auth header exists without requiring it
        from flask_jwt_extended import decode_token
        auth_header = request.headers.get("Authorization")
        if auth_header:
            token = auth_header.split(" ")[1]
            decoded = decode_token(token)
            user_id = decoded["sub"]
    except:
        pass

    event = UserEvent(
        user_id=user_id,
        event_type=data.get("event_type"),
        payload=data.get("payload", {})
    )
    db.session.add(event)
    db.session.commit()
    
    return jsonify({"status": "tracked"}), 201

@router.route("/bookmarks", methods=["POST"])
@jwt_required()
def add_bookmark():
    user_id = get_jwt_identity()
    data = request.get_json()
    
    bookmark = Bookmark(user_id=user_id, place_id=data["place_id"])
    db.session.add(bookmark)
    db.session.commit()
    
    # Also track as an event for analytics
    event = UserEvent(user_id=user_id, event_type="bookmark", payload={"place_id": data["place_id"]})
    db.session.add(event)
    db.session.commit()
    
    return jsonify({"message": "Bookmarked"}), 201

@router.route("/dashboard", methods=["GET"])
@jwt_required()
def get_dashboard():
    # In production, check for ADMIN role
    from src.services.analytics_service import analytics_service
    metrics = analytics_service.get_dashboard_metrics()
    quality = analytics_service.get_data_quality_metrics()
    
    return jsonify({
        "product_metrics": metrics,
        "data_quality": quality
    })
