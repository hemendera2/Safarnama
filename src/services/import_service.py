import pandas as pd

from src.models import Category, City, Place, State, db
from src.utils.logger import logger


class ImportService:
    @staticmethod
    def import_from_csv(file_path, source="Manual Import"):
        logger.info(f"Starting bulk import from {file_path} via {source}")
        df = pd.read_csv(file_path)
        success_count = 0
        duplicate_count = 0
        errors = []

        for index, row in df.iterrows():
            try:
                data = row.to_dict()

                # 1. Basic Deduplication Logic (Name + State proximity)
                existing = Place.query.filter(
                    Place.name.ilike(data["name"].strip()),
                    Place.latitude.between(
                        float(data["latitude"]) - 0.01, float(data["latitude"]) + 0.01
                    ),
                ).first()

                if existing:
                    duplicate_count += 1
                    continue

                # 2. Dependency Lookup
                state = State.query.filter_by(name=data["state_name"]).first()
                city = City.query.filter_by(name=data["city_name"]).first()
                category = Category.query.filter_by(name=data["category_name"]).first()

                if not (state and city and category):
                    # In production, we'd auto-create missing geography
                    raise ValueError(f"Missing references for {data['name']}")

                place = Place(
                    name=data["name"].strip(),
                    state_id=state.id,
                    city_id=city.id,
                    category_id=category.id,
                    latitude=float(data["latitude"]),
                    longitude=float(data["longitude"]),
                    description=data["description"],
                    best_time_to_visit=data.get("best_time", "Year round"),
                    crowd_factor=int(data.get("crowd_factor", 1)),
                    source_attribution=source,
                    confidence_score=data.get(
                        "confidence", 0.8
                    ),  # Default to 0.8 for new imports
                )
                db.session.add(place)
                success_count += 1
            except Exception as e:
                errors.append({"row": index, "error": str(e)})

        try:
            db.session.commit()
            logger.info(
                f"Import complete: {success_count} success, {duplicate_count} skipped, {len(errors)} failed."
            )
        except Exception as e:
            db.session.rollback()
            logger.error("Transaction failed", error=str(e))

        return {
            "success": success_count,
            "duplicates": duplicate_count,
            "errors": errors,
        }


import_service = ImportService()
