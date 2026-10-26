import os
import logging
from flask import Flask, render_template, jsonify
from config import config_by_name
from app.extensions import db
from app.utils.file_helpers import format_bytes, shorten_hash, get_file_type_category, get_file_icon_class

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


def create_app(config_name=None):
    """
    Application Factory for CloudDedup.
    Configures database, registers blueprints, registers context helpers and error handlers.
    """
    if config_name is None:
        config_name = os.environ.get("FLASK_ENV", "default")

    server = Flask(__name__)
    server.config.from_object(config_by_name.get(config_name, config_by_name["default"]))

    # Pre-check database connectivity to ensure clean startup
    db_uri = server.config.get("SQLALCHEMY_DATABASE_URI", "")
    if db_uri.startswith("mysql") and not server.config.get("TESTING", False):
        import pymysql
        import time

        host = server.config.get("MYSQL_HOST", "127.0.0.1")
        port = int(server.config.get("MYSQL_PORT", 3306))
        user = server.config.get("MYSQL_USER", "root")
        password = server.config.get("MYSQL_PASSWORD", "")
        db_name = server.config.get("MYSQL_DATABASE", "clouddedup_db")

        connected = False
        last_err = None
        for attempt in range(1, 4):
            try:
                conn = pymysql.connect(
                    host=host,
                    port=port,
                    user=user,
                    password=password,
                    connect_timeout=3,
                )
                with conn.cursor() as cur:
                    cur.execute(
                        f"CREATE DATABASE IF NOT EXISTS `{db_name}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
                    )
                conn.close()
                logger.info(f"MySQL connected successfully to '{db_name}' on {host}:{port}.")
                connected = True
                break
            except Exception as e:
                last_err = e
                logger.warning(f"MySQL connection attempt {attempt} failed ({e}). Retrying in 1s...")
                time.sleep(1)

        if not connected:
            logger.error(
                f"FATAL: MySQL server is not accessible on {host}:{port}. Error: {last_err}\n"
                "Please verify that MySQL is started in XAMPP Control Panel!"
            )
            raise RuntimeError(
                f"Could not connect to MySQL at {host}:{port} ({last_err}). "
                "Please make sure MySQL is started in XAMPP Control Panel."
            )

    # Initialize extensions
    db.init_app(server)

    # Initialize database tables
    with server.app_context():
        import app.models  # noqa: F401
        try:
            db.create_all()
            logger.info("Database schema initialized successfully.")
        except Exception as e:
            logger.error(f"Error creating database tables: {e}")

    # Register Blueprints
    from app.routes.auth_routes import auth_bp
    from app.routes.dashboard_routes import dashboard_bp
    from app.routes.upload_routes import upload_bp
    from app.routes.file_routes import file_bp
    from app.routes.duplicate_routes import duplicate_bp
    from app.routes.statistics_routes import statistics_bp

    server.register_blueprint(auth_bp)
    server.register_blueprint(dashboard_bp)
    server.register_blueprint(upload_bp)
    server.register_blueprint(file_bp)
    server.register_blueprint(duplicate_bp)
    server.register_blueprint(statistics_bp)

    # Jinja Template Context Processors & Filters
    @server.context_processor
    def inject_helpers():
        return {
            "format_bytes": format_bytes,
            "shorten_hash": shorten_hash,
            "get_file_type_category": get_file_type_category,
            "get_file_icon_class": get_file_icon_class,
            "firebase_project_id": server.config.get("FIREBASE_PROJECT_ID", ""),
        }

    # Custom Error Handlers
    @server.errorhandler(404)
    def page_not_found(e):
        return render_template("errors/404.html"), 404

    @server.errorhandler(413)
    def request_entity_too_large(e):
        return (
            jsonify({
                "success": False,
                "error": "The uploaded file exceeds the maximum allowed size limit.",
            }),
            413,
        )

    @server.errorhandler(500)
    def internal_server_error(e):
        logger.error(f"Internal server error: {e}")
        return render_template("errors/500.html"), 500

    return server


# Fallback instance for WSGI servers referencing app:app
app = create_app(os.environ.get("FLASK_ENV", "production"))
