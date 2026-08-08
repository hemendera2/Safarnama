import json
import pytest
from src.models import User, Itinerary, db

def test_itinerary_lifecycle(client, app):
    with app.app_context():
        user = User(email="planner@safarnama.in")
        user.set_password("pass")
        db.session.add(user)
        db.session.commit()

        login_res = client.post('/api/v1/auth/login', json={"email": "planner@safarnama.in", "password": "pass"})
        token = login_res.get_json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # 1. Create Itinerary
        create_res = client.post('/api/v1/itinerary/', json={"title": "My Road Trip"}, headers=headers)
        assert create_res.status_code == 201
        it_id = create_res.get_json()["id"]

        # 2. Get Itineraries
        list_res = client.get('/api/v1/itinerary/', headers=headers)
        assert list_res.status_code == 200
        assert len(list_res.get_json()) == 1

        # 3. Get Specific Itinerary
        get_res = client.get(f'/api/v1/itinerary/{it_id}', headers=headers)
        assert get_res.status_code == 200
        assert get_res.get_json()["title"] == "My Road Trip"

def test_itinerary_stops(client, app):
    with app.app_context():
        # Setup data
        from src.models import User, Itinerary, Place, Country, State, District, City, Category
        user = User(email="stops@safarnama.in")
        user.set_password("pass")
        india = Country(name="IndiaStops", code="IS")
        db.session.add(india)
        db.session.flush()
        s = State(name="SStops", country_id=india.id, region="North")
        db.session.add(s)
        db.session.flush()
        d = District(name="DStops", state_id=s.id)
        db.session.add(d)
        db.session.flush()
        c = City(name="CStops", district_id=d.id)
        db.session.add(c)
        db.session.flush()
        cat = Category(name="CatStops")
        db.session.add(cat)
        db.session.flush()
        p = Place(name="PStops", state_id=s.id, city_id=c.id, category_id=cat.id, 
                  latitude=1.0, longitude=1.0, description="D", best_time_to_visit="B", crowd_factor=1)
        it = Itinerary(user=user, title="Trip")
        db.session.add_all([user, p, it])
        db.session.commit()

        login_res = client.post('/api/v1/auth/login', json={"email": "stops@safarnama.in", "password": "pass"})
        token = login_res.get_json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # 1. Add Stop
        add_res = client.post(f'/api/v1/itinerary/{it.id}/stops', json={"place_id": p.id}, headers=headers)
        assert add_res.status_code == 201
        
        # 2. Verify Stop
        it_res = client.get(f'/api/v1/itinerary/{it.id}', headers=headers)
        assert len(it_res.get_json()["stops"]) == 1
