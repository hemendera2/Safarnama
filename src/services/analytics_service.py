from sqlalchemy import func, desc
from src.models import db, UserEvent, Bookmark, Place
from datetime import datetime, timedelta

class ProductAnalyticsService:
    @staticmethod
    def get_dashboard_metrics():
        """
        Calculates North Star metrics for Safarnama.
        """
        metrics = {}
        
        # 1. Search Success Rate (Queries with results vs Zero-results)
        total_searches = UserEvent.query.filter_by(event_type="search").count()
        zero_results = UserEvent.query.filter_by(event_type="no_results").count()
        metrics["search_success_rate"] = round(((total_searches - zero_results) / total_searches * 100), 2) if total_searches > 0 else 0
        
        # 2. Recommendation Acceptance (Clicks / Searches)
        total_clicks = UserEvent.query.filter_by(event_type="click").count()
        metrics["recommendation_ctr"] = round((total_clicks / total_searches * 100), 2) if total_searches > 0 else 0
        
        # 3. Destination Desirability (Bookmarks)
        metrics["total_bookmarks"] = Bookmark.query.count()
        
        # 4. Top Search Intent (by Context)
        top_interests = db.session.query(
            func.json_extract(UserEvent.payload, '$.interest').label('interest'),
            func.count(UserEvent.id).label('count')
        ).filter(UserEvent.event_type == 'search').group_by('interest').order_by(desc('count')).limit(5).all()
        metrics["top_interests"] = [dict(row._mapping) for row in top_interests]

        return metrics

    @staticmethod
    def get_data_quality_metrics():
        """
        Measures the quality of the Travel Knowledge Graph.
        """
        total_places = Place.query.count()
        avg_confidence = db.session.query(func.avg(Place.confidence_score)).scalar() or 0
        
        # Places missing metadata (e.g., description or history)
        missing_metadata = Place.query.filter((Place.description == None) | (Place.description == '')).count()
        
        return {
            "total_destinations": total_places,
            "average_confidence": round(avg_confidence, 2),
            "completeness_score": round(((total_places - missing_metadata) / total_places * 100), 2) if total_places > 0 else 0
        }

analytics_service = ProductAnalyticsService()
