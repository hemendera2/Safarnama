from src.models import (
    Category,
    City,
    Country,
    District,
    IntelligenceScore,
    Place,
    State,
)
from src.services.recommendation_engine import recommendation_engine


def test_ranking_influence(app, db):
    with app.app_context():
        # Setup minimal data for ranking test
        india = Country(name="India", code="IN")
        db.session.add(india)
        db.session.flush()

        state = State(name="Test State", region="North", country_id=india.id)
        db.session.add(state)
        db.session.flush()

        district = District(name="Test District", state_id=state.id)
        db.session.add(district)
        db.session.flush()

        city = City(name="Test City", district_id=district.id)
        db.session.add(city)
        db.session.flush()

        cat = Category(name="Nature")
        db.session.add(cat)
        db.session.flush()

        # Place A: Strong Photography, Weak Adventure
        p1 = Place(
            name="Photo Spot",
            state_id=state.id,
            city_id=city.id,
            category_id=cat.id,
            latitude=10.0,
            longitude=10.0,
            description="desc",
            best_time_to_visit="Monsoon",
            crowd_factor=3,
        )
        p1.intelligence = IntelligenceScore(
            photography=0.9, adventure=0.1, monsoon_value=0.8
        )

        # Place B: Strong Adventure, Weak Photography
        p2 = Place(
            name="Adventure Spot",
            state_id=state.id,
            city_id=city.id,
            category_id=cat.id,
            latitude=11.0,
            longitude=11.0,
            description="desc",
            best_time_to_visit="Winter",
            crowd_factor=3,
        )
        p2.intelligence = IntelligenceScore(
            photography=0.1, adventure=0.9, winter_value=0.8
        )

        db.session.add_all([p1, p2])
        db.session.commit()

        # Test Photography Context
        res_photo = recommendation_engine.rank_places(
            [p1, p2], {"interest": "photography", "season": "monsoon"}
        )
        assert res_photo[0]["place"]["name"] == "Photo Spot"

        # Test Adventure Context
        res_adv = recommendation_engine.rank_places(
            [p1, p2], {"vibe": "adventure", "season": "winter"}
        )
        assert res_adv[0]["place"]["name"] == "Adventure Spot"
