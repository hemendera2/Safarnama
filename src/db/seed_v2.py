from src.app_factory import create_app
from src.models import db, Country, State, District, City, Village, Category, SubCategory, Tag, Activity, Place, User, UserRole, NodeRelationship, RelationshipType
import os

app = create_app()

def seed():
    with app.app_context():
        print("Starting Knowledge Graph seed...")
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
        adventure = Category(name="Adventure")
        db.session.add_all([nature, adventure])
        db.session.flush()

        waterfall = SubCategory(name="Waterfall", category_id=nature.id)
        meadow = SubCategory(name="Meadow", category_id=nature.id)
        db.session.add_all([waterfall, meadow])
        db.session.flush()

        # Tags
        offbeat = Tag(name="Offbeat")
        hidden = Tag(name="Hidden Gem")
        monsoon = Tag(name="Monsoon Spot")
        db.session.add_all([offbeat, hidden, monsoon])
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
        phe_phe.tags.extend([offbeat, hidden, monsoon])

        shangarh = Place(
            name="Shangarh Meadows",
            state_id=hp.id, city_id=sainj.id,
            category_id=nature.id, subcategory_id=meadow.id,
            latitude=31.6789, longitude=77.3512,
            description="A vast, high-altitude meadow surrounded by deodar forests.",
            best_time_to_visit="April to June",
            crowd_factor=1
        )
        shangarh.tags.extend([offbeat, hidden])
        
        krang_shuri = Place(
            name="Krang Suri Falls",
            state_id=meg.id, city_id=jowai.id,
            category_id=nature.id, subcategory_id=waterfall.id,
            latitude=25.3475, longitude=92.5312,
            description="Famous for its turquoise blue water.",
            best_time_to_visit="September to April",
            crowd_factor=3
        )
        krang_shuri.tags.extend([offbeat, monsoon])

        db.session.add_all([phe_phe, shangarh, krang_shuri])
        db.session.flush()

        # Edges: Knowledge Graph Relationships
        rel1 = NodeRelationship(
            source_id=phe_phe.id,
            target_id=krang_shuri.id,
            rel_type=RelationshipType.NEAR,
            weight=0.9
        )
        rel2 = NodeRelationship(
            source_id=phe_phe.id,
            target_id=krang_shuri.id,
            rel_type=RelationshipType.RECOMMENDED_TOGETHER,
            weight=0.8
        )
        
        db.session.add_all([rel1, rel2])
        db.session.commit()
        print("Knowledge Graph Seeded Successfully!")

if __name__ == "__main__":
    seed()
