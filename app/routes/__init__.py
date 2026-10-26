from app.routes.auth_routes import auth_bp
from app.routes.dashboard_routes import dashboard_bp
from app.routes.upload_routes import upload_bp
from app.routes.file_routes import file_bp
from app.routes.duplicate_routes import duplicate_bp
from app.routes.statistics_routes import statistics_bp

__all__ = [
    "auth_bp",
    "dashboard_bp",
    "upload_bp",
    "file_bp",
    "duplicate_bp",
    "statistics_bp",
]
