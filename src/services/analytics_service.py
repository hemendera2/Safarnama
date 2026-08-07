from datetime import datetime, timedelta

from sqlalchemy import desc, func

from src.models import Bookmark, Place, UserEvent, db


class ProductAnalyticsService:
    @staticmethod
    def _get_base_query():
        """Base query for all product metrics: excludes test sessions."""
        return UserEvent.query.filter_by(test_session=False)

    @staticmethod
    def calculate_tdr_v1():
        """
        Implementation of Trusted Discovery Rate v1.0
        Enforces 30-minute session window and destination-specific funnel integrity.
        """
        # Get all non-test events
        events = (
            ProductAnalyticsService._get_base_query()
            .order_by(UserEvent.session_id, UserEvent.timestamp)
            .all()
        )

        sessions = {}
        for e in events:
            if e.session_id not in sessions:
                sessions[e.session_id] = []
            sessions[e.session_id].append(e)

        eligible_count = 0
        success_count = 0
        window_delta = timedelta(minutes=30)

        for _session_id, s_events in sessions.items():
            # Step 1: Filter events within 30-minute window of the first search
            search_events = [e for e in s_events if e.event_type == "search"]
            if not search_events:
                continue

            first_search_time = search_events[0].timestamp
            # In eligibility, we count the session if it has ANY valid search
            eligible_count += 1

            # Funnel analysis per destination within the 30-min window
            # Path: Search -> Open X -> Trust X -> Bookmark X
            valid_window_events = [
                e for e in s_events if e.timestamp <= first_search_time + window_delta
            ]

            # Track which destinations achieved 'open' and 'trust'
            destinations_opened = set()
            destinations_trusted = set()
            success_found = False

            for e in valid_window_events:
                if e.timestamp < first_search_time:
                    continue  # Skip pre-search events for funnel

                place_id = e.payload.get("place_id") if e.payload else None

                if e.event_type == "destination_open" and place_id:
                    destinations_opened.add(place_id)
                elif (
                    e.event_type == "trust_interaction"
                    and place_id in destinations_opened
                ):
                    destinations_trusted.add(place_id)
                elif e.event_type == "bookmark" and place_id in destinations_trusted:
                    success_found = True
                    break

            if success_found:
                success_count += 1

        rate = round(success_count / eligible_count, 4) if eligible_count > 0 else None

        return {
            "metric": "trusted_discovery_rate",
            "version": "1.0",
            "successful_sessions": success_count,
            "eligible_sessions": eligible_count,
            "rate": rate,
            "status": "sufficient_data" if eligible_count >= 5 else "insufficient_data",
            "window_minutes": 30,
        }

    @staticmethod
    def get_dashboard_metrics():
        metrics = {}
        tdr = ProductAnalyticsService.calculate_tdr_v1()
        metrics["tdr_v1"] = tdr

        base_q = ProductAnalyticsService._get_base_query()

        # 1. Search Success Rate
        total_searches = base_q.filter_by(event_type="search").count()
        zero_results = base_q.filter_by(event_type="no_results").count()
        metrics["search_success_rate"] = (
            round(((total_searches - zero_results) / total_searches * 100), 2)
            if total_searches > 0
            else 0
        )
        metrics["search_counts"] = {"total": total_searches, "zero": zero_results}

        # 2. Recommendation CTR (Impression -> Click)
        total_impressions = base_q.filter_by(event_type="recommendation_impression").count()
        total_clicks = base_q.filter_by(event_type="recommendation_click").count()
        metrics["recommendation_ctr"] = (
            round((total_clicks / total_impressions * 100), 2) if total_impressions > 0 else 0
        )
        metrics["ctr_counts"] = {"impressions": total_impressions, "clicks": total_clicks}

        # 3. Funnel Breakdown
        metrics["funnel"] = {
            "search": total_searches,
            "open": base_q.filter_by(event_type="destination_open").count(),
            "trust": base_q.filter_by(event_type="trust_interaction").count(),
            "bookmark": base_q.filter_by(event_type="bookmark").count()
        }

        metrics["total_bookmarks"] = Bookmark.query.count()

        top_interests = (
            db.session.query(
                func.json_extract(UserEvent.payload, "$.interest").label("interest"),
                func.count(UserEvent.id).label("count"),
            )
            .filter(UserEvent.event_type == "search", UserEvent.test_session == False)
            .group_by("interest")
            .order_by(desc("count"))
            .limit(5)
            .all()
        )
        metrics["top_interests"] = [dict(row._mapping) for row in top_interests]

        return metrics

    @staticmethod
    def get_data_quality_metrics():
        """
        Comprehensive Health Report for the Travel Knowledge Graph.
        """
        total_places = Place.query.count()
        if total_places == 0:
            return {"status": "empty"}

        # 1. Coverage
        coverage = {
            "total_nodes": total_places,
            "connected_nodes": db.session.query(Place).join(Place.outgoing_relationships).distinct().count(),
            "states_covered": db.session.query(Place.state_id).distinct().count()
        }

        # 2. Metadata Depth
        def completeness(field):
            return round(Place.query.filter(field != None, field != '').count() / total_places * 100, 1)

        depth = {
            "description": completeness(Place.description),
            "history": completeness(Place.history),
            "coordinates": completeness(Place.latitude),
            "infrastructure": completeness(Place.facilities)
        }

        # 3. Trust & Freshness
        avg_confidence = db.session.query(func.avg(Place.confidence_score)).scalar() or 0
        
        now = datetime.utcnow()
        fresh_count = Place.query.filter(Place.last_verified_at > now - timedelta(days=90)).count()
        stale_count = Place.query.filter(Place.last_verified_at <= now - timedelta(days=180)).count()

        return {
            "coverage": coverage,
            "metadata_depth": depth,
            "average_confidence": round(avg_confidence, 2),
            "freshness": {
                "fresh_rate": round(fresh_count / total_places * 100, 1),
                "stale_rate": round(stale_count / total_places * 100, 1)
            }
        }


analytics_service = ProductAnalyticsService()
