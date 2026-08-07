from flask import Flask, send_from_directory
from flask_cors import CORS
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_talisman import Talisman
from prometheus_flask_exporter import PrometheusMetrics
from src.core.config import settings
from src.models import db
from src.utils.observability import setup_observability
from src.utils.logger import logger as struct_logger
import os

def create_app():
    app = Flask(__name__, static_folder='../static')
    app.config["SQLALCHEMY_DATABASE_URI"] = settings.DATABASE_URL
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SECRET_KEY"] = settings.SECRET_KEY
    app.config["JWT_SECRET_KEY"] = settings.SECRET_KEY

    # Security Headers
    Talisman(app, content_security_policy=None, force_https=False)

    # Initialize Extensions
    db.init_app(app)
    Migrate(app, db)
    CORS(app)
    JWTManager(app)
    
    # Rate Limiting
    limiter = Limiter(
        get_remote_address,
        app=app,
        default_limits=["200 per day", "50 per hour"],
        storage_uri="memory://",
    )

    # Observability
    setup_observability(app)
    metrics = PrometheusMetrics(app)
    metrics.info('app_info', 'Application info', version='2.1.0')

    struct_logger.info("Initializing Safarnama Production API...")

    # Register Blueprints
    from src.api.v1.endpoints import api_router
    app.register_blueprint(api_router, url_prefix=settings.API_V1_STR)

    @app.route("/")
    def index():
        return send_from_directory(app.static_folder, 'index.html')

    @app.route("/admin/insights")
    def admin():
        return send_from_directory(app.static_folder, 'admin.html')

    @app.route("/health")
    def health_check():
        try:
            # Check DB connection
            db.session.execute(db.text('SELECT 1'))
            return {"status": "healthy", "database": "connected"}
        except Exception as e:
            struct_logger.error("Health check failed", error=str(e))
            return {"status": "unhealthy", "database": "disconnected"}, 500

    return app
