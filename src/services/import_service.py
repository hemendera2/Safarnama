import pandas as pd
from src.models import db, Place, State, City, Category, SubCategory
from src.utils.data_quality import LocationValidationSchema
from src.utils.logger import logger

class ImportService:
    @staticmethod
    def import_from_csv(file_path):
        logger.info(f"Starting bulk import from {file_path}")
        df = pd.read_csv(file_path)
        success_count = 0
        errors = []

        for index, row in df.iterrows():
            try:
                # 1. Validate data structure
                data = row.to_dict()
                # Simplified validation for demo
                # In production, we'd map column names properly
                
                # 2. Check dependencies (Simplified lookup)
                state = State.query.filter_by(name=data['state_name']).first()
                city = City.query.filter_by(name=data['city_name']).first()
                category = Category.query.filter_by(name=data['category_name']).first()
                
                if not (state and city and category):
                    raise ValueError(f"Missing references: State={state}, City={city}, Category={category}")

                place = Place(
                    name=data['name'],
                    state_id=state.id,
                    city_id=city.id,
                    category_id=category.id,
                    latitude=float(data['latitude']),
                    longitude=float(data['longitude']),
                    description=data['description'],
                    best_time_to_visit=data.get('best_time', 'Year round'),
                    crowd_factor=int(data.get('crowd_factor', 1))
                )
                db.session.add(place)
                success_count += 1
            except Exception as e:
                errors.append({"row": index, "error": str(e)})

        try:
            db.session.commit()
            logger.info(f"Import complete: {success_count} success, {len(errors)} failed.")
        except Exception as e:
            db.session.rollback()
            logger.error("Transaction failed, rolling back", error=str(e))
            
        return {"success": success_count, "errors": errors}

import_service = ImportService()
