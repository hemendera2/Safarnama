from datetime import datetime, timedelta

from src.models import UserEvent, db


def test_tdr_v1_integrity(client, app):
    with app.app_context():
        # Clear existing events
        db.session.query(UserEvent).delete()
        db.session.commit()

        base_time = datetime.utcnow()

        # 1. SUCCESS: Search -> Open A -> Trust A -> Bookmark A (All within 5 min)
        s1 = "session-success"
        db.session.add_all(
            [
                UserEvent(
                    session_id=s1,
                    event_type="search",
                    timestamp=base_time,
                    test_session=False,
                ),
                UserEvent(
                    session_id=s1,
                    event_type="destination_open",
                    payload={"place_id": "A"},
                    timestamp=base_time + timedelta(minutes=1),
                    test_session=False,
                ),
                UserEvent(
                    session_id=s1,
                    event_type="trust_interaction",
                    payload={"place_id": "A"},
                    timestamp=base_time + timedelta(minutes=2),
                    test_session=False,
                ),
                UserEvent(
                    session_id=s1,
                    event_type="bookmark",
                    payload={"place_id": "A"},
                    timestamp=base_time + timedelta(minutes=3),
                    test_session=False,
                ),
            ]
        )

        # 2. FAILURE: No Trust (Search -> Open B -> Bookmark B)
        s2 = "session-no-trust"
        db.session.add_all(
            [
                UserEvent(
                    session_id=s2,
                    event_type="search",
                    timestamp=base_time,
                    test_session=False,
                ),
                UserEvent(
                    session_id=s2,
                    event_type="destination_open",
                    payload={"place_id": "B"},
                    timestamp=base_time + timedelta(minutes=1),
                    test_session=False,
                ),
                UserEvent(
                    session_id=s2,
                    event_type="bookmark",
                    payload={"place_id": "B"},
                    timestamp=base_time + timedelta(minutes=2),
                    test_session=False,
                ),
            ]
        )

        # 3. FAILURE: Wrong Order (Search -> Trust A -> Open A -> Bookmark A)
        s3 = "session-wrong-order"
        db.session.add_all(
            [
                UserEvent(
                    session_id=s3,
                    event_type="search",
                    timestamp=base_time,
                    test_session=False,
                ),
                UserEvent(
                    session_id=s3,
                    event_type="trust_interaction",
                    payload={"place_id": "C"},
                    timestamp=base_time + timedelta(minutes=1),
                    test_session=False,
                ),
                UserEvent(
                    session_id=s3,
                    event_type="destination_open",
                    payload={"place_id": "C"},
                    timestamp=base_time + timedelta(minutes=2),
                    test_session=False,
                ),
                UserEvent(
                    session_id=s3,
                    event_type="bookmark",
                    payload={"place_id": "C"},
                    timestamp=base_time + timedelta(minutes=3),
                    test_session=False,
                ),
            ]
        )

        # 4. FAILURE: Different Destination (Search -> Open D -> Trust D -> Bookmark E)
        s4 = "session-diff-dest"
        db.session.add_all(
            [
                UserEvent(
                    session_id=s4,
                    event_type="search",
                    timestamp=base_time,
                    test_session=False,
                ),
                UserEvent(
                    session_id=s4,
                    event_type="destination_open",
                    payload={"place_id": "D"},
                    timestamp=base_time + timedelta(minutes=1),
                    test_session=False,
                ),
                UserEvent(
                    session_id=s4,
                    event_type="trust_interaction",
                    payload={"place_id": "D"},
                    timestamp=base_time + timedelta(minutes=2),
                    test_session=False,
                ),
                UserEvent(
                    session_id=s4,
                    event_type="bookmark",
                    payload={"place_id": "E"},
                    timestamp=base_time + timedelta(minutes=3),
                    test_session=False,
                ),
            ]
        )

        # 5. FAILURE: >30 MIN WINDOW (Search at T0, Open at T+31m)
        s5 = "session-late"
        db.session.add_all(
            [
                UserEvent(
                    session_id=s5,
                    event_type="search",
                    timestamp=base_time,
                    test_session=False,
                ),
                UserEvent(
                    session_id=s5,
                    event_type="destination_open",
                    payload={"place_id": "F"},
                    timestamp=base_time + timedelta(minutes=31),
                    test_session=False,
                ),
                UserEvent(
                    session_id=s5,
                    event_type="trust_interaction",
                    payload={"place_id": "F"},
                    timestamp=base_time + timedelta(minutes=32),
                    test_session=False,
                ),
                UserEvent(
                    session_id=s5,
                    event_type="bookmark",
                    payload={"place_id": "F"},
                    timestamp=base_time + timedelta(minutes=33),
                    test_session=False,
                ),
            ]
        )

        # 6. EXCLUDED: Test Session (test_session=True)
        s6 = "session-test"
        db.session.add_all(
            [
                UserEvent(
                    session_id=s6,
                    event_type="search",
                    timestamp=base_time,
                    test_session=True,
                ),
                UserEvent(
                    session_id=s6,
                    event_type="destination_open",
                    payload={"place_id": "G"},
                    timestamp=base_time + timedelta(minutes=1),
                    test_session=True,
                ),
                UserEvent(
                    session_id=s6,
                    event_type="trust_interaction",
                    payload={"place_id": "G"},
                    timestamp=base_time + timedelta(minutes=2),
                    test_session=True,
                ),
                UserEvent(
                    session_id=s6,
                    event_type="bookmark",
                    payload={"place_id": "G"},
                    timestamp=base_time + timedelta(minutes=3),
                    test_session=True,
                ),
            ]
        )

        # 7. INELIGIBLE: No Search
        s7 = "session-no-search"
        db.session.add_all(
            [
                UserEvent(
                    session_id=s7,
                    event_type="destination_open",
                    payload={"place_id": "H"},
                    timestamp=base_time,
                    test_session=False,
                ),
                UserEvent(
                    session_id=s7,
                    event_type="trust_interaction",
                    payload={"place_id": "H"},
                    timestamp=base_time + timedelta(minutes=1),
                    test_session=False,
                ),
                UserEvent(
                    session_id=s7,
                    event_type="bookmark",
                    payload={"place_id": "H"},
                    timestamp=base_time + timedelta(minutes=2),
                    test_session=False,
                ),
            ]
        )

        db.session.commit()

        from src.services.analytics_service import analytics_service

        tdr = analytics_service.calculate_tdr_v1()

        # Eligible: s1, s2, s3, s4, s5 (Total 5)
        # Successful: s1 (Total 1)
        # Rate: 0.2
        assert tdr["eligible_sessions"] == 5
        assert tdr["successful_sessions"] == 1
        assert tdr["rate"] == 0.2
