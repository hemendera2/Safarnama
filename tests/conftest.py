import pytest
from src.app_factory import create_app
from src.models import db as _db
from src.core.config import settings
import os

@pytest.fixture(scope='session')
def app():
    # Use a separate test database
    test_db_path = os.path.join(os.getcwd(), 'db/test_safarnama.db')
    settings.DATABASE_URL = f"sqlite:///{test_db_path}"
    
    app = create_app()
    app.config.update({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": settings.DATABASE_URL
    })

    with app.app_context():
        _db.create_all()
        yield app
        _db.drop_all()
        if os.path.exists(test_db_path):
            os.remove(test_db_path)

@pytest.fixture(scope='function')
def db(app):
    with app.app_context():
        yield _db
        _db.session.rollback()
        # Clean up tables between tests if needed, or just rollback
        for table in reversed(_db.metadata.sorted_tables):
            _db.session.execute(table.delete())
        _db.session.commit()

@pytest.fixture
def client(app):
    return app.test_client()
