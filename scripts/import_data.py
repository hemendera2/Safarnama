import os
import sys

from src.app_factory import create_app
from src.services.import_service import import_service

app = create_app()


def run_import(csv_path):
    if not os.path.exists(csv_path):
        print(f"File not found: {csv_path}")
        return

    with app.app_context():
        print(f"--- Starting Import from {csv_path} ---")
        result = import_service.import_from_csv(csv_path)
        print(
            f"Import Result: {result['success']} success, {len(result['errors'])} failed."
        )
        for err in result["errors"]:
            print(f"  Row {err['row']}: {err['error']}")


if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else "data/sample_places.csv"
    run_import(path)
