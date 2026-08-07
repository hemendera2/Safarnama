from flask import Blueprint
from .places import router as places_router
from .auth import router as auth_router

api_router = Blueprint("api_v1", __name__)
api_router.register_blueprint(places_router, url_prefix="/places")
api_router.register_blueprint(auth_router, url_prefix="/auth")
