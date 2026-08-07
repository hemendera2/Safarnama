import json
import pytest
from src.models import User, Place, db, Bookmark

def test_persistent_bookmarks(client, app):
    with app.app_context():
        # 1. Setup User and Place
        user = User(email="test@bookmark.com")
        user.set_password("pass")
        
        # Need minimal Place data
        from src.models import Country, State, District, City, Category
        india = Country(name="India", code="IN")
        db.session.add(india)
        db.session.flush()
        s = State(name="S", country_id=india.id, region="North")
        db.session.add(s)
        db.session.flush()
        d = District(name="D", state_id=s.id)
        db.session.add(d)
        db.session.flush()
        c = City(name="C", district_id=d.id)
        db.session.add(c)
        db.session.flush()
        cat = Category(name="Cat")
        db.session.add(cat)
        db.session.flush()

        p = Place(name="P", state_id=s.id, city_id=c.id, category_id=cat.id, 
                  latitude=1.0, longitude=1.0, description="D", best_time_to_visit="B", crowd_factor=1)
        db.session.add_all([user, p])
        db.session.commit()

        # 2. Login
        login_res = client.post('/api/v1/auth/login', json={"email": "test@bookmark.com", "password": "pass"})
        token = login_res.get_json()["access_token"]

        # 3. Bookmark
        response = client.post('/api/v1/analytics/bookmarks', 
                               json={"place_id": p.id, "session_id": "test-session"},
                               headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 201

        # 4. Verify Persistence
        assert Bookmark.query.filter_by(user_id=user.id, place_id=p.id).count() == 1

        # 5. Duplicate Handling
        dup_response = client.post('/api/v1/analytics/bookmarks', 
                                   json={"place_id": p.id, "session_id": "test-session"},
                                   headers={"Authorization": f"Bearer {token}"})
        assert dup_response.status_code == 200
        assert Bookmark.query.filter_by(user_id=user.id, place_id=p.id).count() == 1
