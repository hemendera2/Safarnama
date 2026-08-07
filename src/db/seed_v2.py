from src.app_factory import create_app
from src.models import db, Country, State, District, City, Village, Category, SubCategory, Tag, Activity, Place, User, UserRole, NodeRelationship, RelationshipType, IntelligenceScore
import os

app = create_app()

def seed():
    with app.app_context():
        print("Starting Intelligence Graph seed...")
        # Clear data (but keep schema)
        meta = db.metadata
        for table in reversed(meta.sorted_tables):
            db.session.execute(table.delete())
        db.session.commit()

        # Users
        admin = User(email="admin@safarnama.in", full_name="System Admin", role=UserRole.ADMIN)
        admin.set_password("admin123")
        db.session.add(admin)
        db.session.flush()

        # Nodes: Geography
        india = Country(name="India", code="IN")
        db.session.add(india)
        db.session.flush()

        meg = State(name="Meghalaya", region="North-East", country_id=india.id)
        hp = State(name="Himachal Pradesh", region="North", country_id=india.id)
        db.session.add_all([meg, hp])
        db.session.flush()

        # Districts & Cities
        wjh = District(name="West Jaintia Hills", state_id=meg.id)
        kullu = District(name="Kullu", state_id=hp.id)
        db.session.add_all([wjh, kullu])
        db.session.flush()

        jowai = City(name="Jowai", district_id=wjh.id, is_offbeat_hub=True)
        sainj = City(name="Sainj", district_id=kullu.id, is_offbeat_hub=True)
        db.session.add_all([jowai, sainj])
        db.session.flush()

        # Classification
        nature = Category(name="Nature")
        db.session.add(nature)
        db.session.flush()

        waterfall = SubCategory(name="Waterfall", category_id=nature.id)
        meadow = SubCategory(name="Meadow", category_id=nature.id)
        db.session.add_all([waterfall, meadow])
        db.session.flush()

        # Places (Nodes)
        phe_phe = Place(
            name="Phe Phe Falls",
            state_id=meg.id, city_id=jowai.id,
            category_id=nature.id, subcategory_id=waterfall.id,
            latitude=25.4410, longitude=92.5165,
            description="A stunning two-tier waterfall hidden in the Jaintia Hills.",
            best_time_to_visit="July to September",
            crowd_factor=2
        )
        
        # Add Intelligence Scores for Phe Phe
        phe_phe_intel = IntelligenceScore(
            photography=0.9, adventure=0.7, offbeat=0.8,
            monsoon_value=1.0, winter_value=0.3
        )
        phe_phe.intelligence = phe_phe_intel

        shangarh = Place(
            name="Shangarh Meadows",
            state_id=hp.id, city_id=sainj.id,
            category_id=nature.id, subcategory_id=meadow.id,
            latitude=31.6789, longitude=77.3512,
            description="A vast, high-altitude meadow surrounded by deodar forests.",
            best_time_to_visit="April to June",
            crowd_factor=1
        )
        shangarh_intel = IntelligenceScore(
            photography=0.8, relaxation=0.9, offbeat=0.7,
            monsoon_value=0.4, summer_value=0.9, winter_value=0.8
        )
        shangarh.intelligence = shangarh_intel

        db.session.add_all([phe_phe, shangarh])
        db.session.commit()
        print("Travel Intelligence Engine Seeded Successfully!")

if __name__ == "__main__":
    seed()
