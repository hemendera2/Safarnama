import enum

from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from src.models import Bookmark, UserEvent, db
from src.utils.auth import admin_required

router = Blueprint("analytics", __name__)


class EventType(enum.Enum):
    SEARCH = "search"
    NO_RESULTS = "no_results"
    RECOMMENDATION_IMPRESSION = "recommendation_impression"
    RECOMMENDATION_CLICK = "recommendation_click"
    DESTINATION_OPEN = "destination_open"
    TRUST_INTERACTION = "trust_interaction"
    BOOKMARK = "bookmark"


@router.route("/event", methods=["POST"])
def track_event():
    data = request.get_json()

    # 1. Strict Event Validation
    try:
        e_type = EventType(data.get("event_type"))
    except ValueError:
        return jsonify({"error": "Invalid event type"}), 400

    # 2. Payload Schema Check
    payload = data.get("payload", {})
    if e_type == EventType.SEARCH and "query" not in payload:
        return jsonify({"error": "Missing search query"}), 400

    user_id = None
    try:
        from flask_jwt_extended import decode_token

        auth_header = request.headers.get("Authorization")
        if auth_header:
            token = auth_header.split(" ")[1]
            decoded = decode_token(token)
            user_id = decoded["sub"]
    except Exception:
        pass

    event = UserEvent(
        user_id=user_id,
        session_id=data.get("session_id", "anonymous"),
        event_type=e_type.value,
        test_session=data.get("test_session", False),
        payload=payload,
    )
    db.session.add(event)
    db.session.commit()

    return jsonify({"status": "tracked"}), 201


@router.route("/bookmarks", methods=["POST"])
@jwt_required()
def add_bookmark():
    user_id = get_jwt_identity()
    data = request.get_json()

    # Check if exists to prevent duplicates
    existing = Bookmark.query.filter_by(
        user_id=user_id, place_id=data["place_id"]
    ).first()
    if existing:
        return jsonify({"message": "Already bookmarked"}), 200

    bookmark = Bookmark(user_id=user_id, place_id=data["place_id"])
    db.session.add(bookmark)
    db.session.commit()

    # Also track as an event for analytics
    event = UserEvent(
        user_id=user_id,
        session_id=data.get("session_id", "auth-session"),
        event_type="bookmark",
        payload={"place_id": data["place_id"]},
    )
    db.session.add(event)
    db.session.commit()

    return jsonify({"message": "Bookmarked"}), 201


@router.route("/dashboard", methods=["GET"])
@admin_required()
def get_dashboard():
    from src.services.analytics_service import analytics_service

    metrics = analytics_service.get_dashboard_metrics()
    quality = analytics_service.get_data_quality_metrics()

    return jsonify({"product_metrics": metrics, "data_quality": quality})
