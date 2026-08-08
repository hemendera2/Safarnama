from typing import Dict, List

from src.models.place import Place


class RecommendationEngine:
    def rank_places(self, places: List[Place], context: Dict) -> List[Dict]:
        """
        Weighted ranking engine for travel discovery.
        Returns ranked places with explainability signals.
        """
        ranked_results = []

        for place in places:
            score = 0.0
            explanations = []

            # 1. Intelligence Score Signal (0.3 weight)
            if place.intelligence:
                intel = place.intelligence
                # Match against context (e.g., 'photography' interest)
                if context.get("interest") == "photography":
                    score += intel.photography * 0.3
                    if intel.photography > 0.8:
                        explanations.append("Exceptional photography potential")

                if context.get("vibe") == "adventure":
                    score += intel.adventure * 0.3
                    if intel.adventure > 0.8:
                        explanations.append("Perfect for adventure seekers")

            # 2. Seasonality Signal (0.3 weight)
            current_season = context.get("season", "monsoon").lower()
            if place.intelligence:
                season_score = getattr(
                    place.intelligence, f"{current_season}_value", 0.5
                )
                score += season_score * 0.3
                if season_score > 0.8:
                    explanations.append(f"Top-rated for {current_season.capitalize()}")

            # 3. Knowledge Graph Connectivity (0.2 weight)
            # Higher weight if it's connected to other popular nodes
            rel_count = len(place.outgoing_relationships)
            if rel_count > 0:
                score += min(rel_count * 0.05, 0.2)
                explanations.append("Part of a rich travel circuit")

            # 4. Crowd Factor Penalty/Bonus (0.2 weight)
            # For offbeat discovery, lower crowd is better
            crowd_score = (5 - place.crowd_factor) / 4.0  # Normalize 1-5 to 1.0-0.0
            score += crowd_score * 0.2
            if place.crowd_factor <= 2:
                explanations.append("Low crowd/Peaceful")

            ranked_results.append(
                {
                    "place": place.to_dict(),
                    "total_score": round(score, 3),
                    "reasons": explanations[:3],  # Top 3 reasons
                }
            )

        # Sort by total score descending
        return sorted(ranked_results, key=lambda x: x["total_score"], reverse=True)


recommendation_engine = RecommendationEngine()
