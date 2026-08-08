from datetime import datetime, timedelta

from src.app_factory import create_app
from src.models import (
    Category,
    City,
    Country,
    District,
    IntelligenceScore,
    NodeRelationship,
    Place,
    RelationshipType,
    State,
    SubCategory,
    User,
    UserRole,
    VerificationLog,
    db,
)

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
        admin = User(
            email="admin@safarnama.in", full_name="System Admin", role=UserRole.ADMIN
        )
        admin.set_password("admin123")
        db.session.add(admin)
        db.session.flush()

        # Nodes: Geography
        india = Country(name="India", code="IN")
        db.session.add(india)
        db.session.flush()

        states_data = [
            ("Meghalaya", "North-East"),
            ("Maharashtra", "West"),
            ("Karnataka", "South"),
            ("Himachal Pradesh", "North"),
            ("Kerala", "South"),
            ("Arunachal Pradesh", "North-East"),
        ]
        states_objs = {}
        for name, region in states_data:
            s = State(name=name, region=region, country_id=india.id)
            db.session.add(s)
            states_objs[name] = s
        db.session.flush()

        # Districts & Cities
        dist_data = [
            ("West Jaintia Hills", "Meghalaya"),
            ("Satara", "Maharashtra"),
            ("Shimoga", "Karnataka"),
            ("Kullu", "Himachal Pradesh"),
            ("Idukki", "Kerala"),
            ("Lower Subansiri", "Arunachal Pradesh"),
        ]
        districts_objs = {}
        for d_name, s_name in dist_data:
            d = District(name=d_name, state_id=states_objs[s_name].id)
            db.session.add(d)
            districts_objs[s_name] = d
        db.session.flush()

        city_data = [
            ("Jowai", "Meghalaya"),
            ("Satara", "Maharashtra"),
            ("Agumbe", "Karnataka"),
            ("Sainj", "Himachal Pradesh"),
            ("Vagamon", "Kerala"),
            ("Ziro", "Arunachal Pradesh"),
        ]
        cities_objs = {}
        for c_name, s_name in city_data:
            c = City(
                name=c_name, district_id=districts_objs[s_name].id, is_offbeat_hub=True
            )
            db.session.add(c)
            cities_objs[c_name] = c
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

        # 1. Phe Phe Falls
        phe_phe = Place(
            name="Phe Phe Falls",
            state_id=states_objs["Meghalaya"].id,
            city_id=cities_objs["Jowai"].id,
            category_id=nature.id,
            subcategory_id=waterfall.id,
            latitude=25.4410,
            longitude=92.5165,
            description="A stunning two-tier waterfall hidden in the Jaintia Hills.",
            best_time_to_visit="July to September",
            crowd_factor=2,
            source_attribution="Government Tourism",
            confidence_score=0.98,
            last_verified_at=datetime.utcnow(),
        )
        phe_phe.intelligence = IntelligenceScore(
            photography=0.9, adventure=0.7, offbeat=0.8, monsoon_value=1.0
        )

        # 2. Shangarh Meadows
        shangarh = Place(
            name="Shangarh Meadows",
            state_id=states_objs["Himachal Pradesh"].id,
            city_id=cities_objs["Sainj"].id,
            category_id=nature.id,
            subcategory_id=meadow.id,
            latitude=31.6789,
            longitude=77.3512,
            description="A vast, high-altitude meadow surrounded by deodar forests.",
            best_time_to_visit="April to June",
            crowd_factor=1,
            source_attribution="Community Verified",
            confidence_score=0.95,
            last_verified_at=datetime.utcnow(),
        )
        shangarh.intelligence = IntelligenceScore(
            photography=0.8, relaxation=0.9, offbeat=0.7, summer_value=0.9
        )

        # 3. Krang Suri
        krang_suri = Place(
            name="Krang Suri Falls",
            state_id=states_objs["Meghalaya"].id,
            city_id=cities_objs["Jowai"].id,
            category_id=nature.id,
            subcategory_id=waterfall.id,
            latitude=25.3475,
            longitude=92.5312,
            description="Famous for its turquoise blue water.",
            best_time_to_visit="September to April",
            crowd_factor=3,
            source_attribution="Government Tourism",
            confidence_score=0.97,
            last_verified_at=datetime.utcnow(),
        )
        krang_suri.intelligence = IntelligenceScore(
            photography=0.9, adventure=0.6, offbeat=0.7, monsoon_value=0.5
        )

        db.session.add_all([phe_phe, shangarh, krang_suri])
        db.session.flush()

        # Relationships
        rel1 = NodeRelationship(
            source_id=phe_phe.id,
            target_id=krang_suri.id,
            rel_type=RelationshipType.NEAR,
            weight=0.9,
        )
        rel2 = NodeRelationship(
            source_id=phe_phe.id,
            target_id=krang_suri.id,
            rel_type=RelationshipType.RECOMMENDED_TOGETHER,
            weight=0.8,
        )

        # Timeline
        v1 = VerificationLog(
            place=phe_phe,
            source="OpenStreetMap",
            summary="Initial coordinates verified",
            verified_at=datetime.utcnow() - timedelta(days=120),
        )
        v2 = VerificationLog(
            place=phe_phe,
            source="Government Tourism",
            summary="Entry fee and accessibility confirmed",
            verified_at=datetime.utcnow() - timedelta(days=90),
        )
        v3 = VerificationLog(
            place=phe_phe,
            source="Community Verified",
            summary="Monsoon flow safety updated",
            verified_at=datetime.utcnow() - timedelta(days=10),
        )

        db.session.add_all([rel1, rel2, v1, v2, v3])
        db.session.commit()
        print("Travel Intelligence, Trust & Graph Seeded Successfully!")


if __name__ == "__main__":
    seed()
