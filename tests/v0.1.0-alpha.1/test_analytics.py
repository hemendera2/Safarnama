import json
import pytest
import uuid
from src.models import UserEvent, db

def test_recommendation_ctr_integrity(client, app):
    with app.app_context():
        # Clear events
        db.session.query(UserEvent).delete()
        db.session.commit()

        # 1. Eligible Sessions (test_session=False)
        s1 = "session-1"
        s2 = "session-2"
        
        db.session.add_all([
            # Session 1: 2 impressions, 1 click
            UserEvent(session_id=s1, event_type="recommendation_impression", payload={"place_id": "A"}, test_session=False),
            UserEvent(session_id=s1, event_type="recommendation_impression", payload={"place_id": "B"}, test_session=False),
            UserEvent(session_id=s1, event_type="recommendation_click", payload={"place_id": "A"}, test_session=False),
            
            # Session 2: 1 impression, 0 clicks
            UserEvent(session_id=s2, event_type="recommendation_impression", payload={"place_id": "C"}, test_session=False),
            
            # Test Session: Should be ignored
            UserEvent(session_id="test", event_type="recommendation_impression", payload={"place_id": "D"}, test_session=True),
            UserEvent(session_id="test", event_type="recommendation_click", payload={"place_id": "D"}, test_session=True)
        ])
        db.session.commit()

        from src.services.analytics_service import analytics_service
        metrics = analytics_service.get_dashboard_metrics()
        
        # Total impressions = 3 (A, B, C)
        # Total clicks = 1 (A)
        # CTR = 1/3 = 33.33%
        assert metrics["recommendation_ctr"] == 33.33
        assert metrics["ctr_counts"]["impressions"] == 3
        assert metrics["ctr_counts"]["clicks"] == 1

def test_event_validation(client):
    # Test invalid event type
    response = client.post('/api/v1/analytics/event', json={
        "event_type": "invalid_type",
        "session_id": "test"
    })
    assert response.status_code == 400
    assert response.get_json()["error"] == "Invalid event type"

    # Test missing search query
    response = client.post('/api/v1/analytics/event', json={
        "event_type": "search",
        "session_id": "test",
        "payload": {}
    })
    assert response.status_code == 400
    assert response.get_json()["error"] == "Missing search query"
