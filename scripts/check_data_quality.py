import sys

from src.app_factory import create_app
from src.models import db
from src.utils.data_quality import validate_db_consistency

app = create_app()


def run_quality_check():
    with app.app_context():
        print("--- Safarnama Data Quality Report ---")
        errors = validate_db_consistency(db.session)
        if not errors:
            print("Status: SUCCESS - All data consistent.")
        else:
            print(f"Status: FAILED - Found {len(errors)} consistency issues.")
            for err in errors:
                print(f"Place ID: {err['place_id']} | Error: {err['error']}")
            sys.exit(1)


if __name__ == "__main__":
    run_quality_check()
