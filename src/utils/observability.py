import uuid
from flask import request, g
from src.utils.logger import logger

def setup_observability(app):
    @app.before_request
    def start_timer():
        g.request_id = request.headers.get("X-Request-Id", str(uuid.uuid4()))
        # You could also track start time here for latency metrics
    
    @app.after_request
    def log_request(response):
        # Structured log for every request
        logger.info(
            "Request processed",
            request_id=getattr(g, "request_id", None),
            method=request.method,
            path=request.path,
            status=response.status_code,
            remote_addr=request.remote_addr
        )
        if hasattr(g, "request_id"):
            response.headers["X-Request-Id"] = g.request_id
        return response
