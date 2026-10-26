import os
from pathlib import Path
from dotenv import load_dotenv

# Base directory of the project
BASE_DIR = Path(__file__).resolve().parent

# Load environment variables from .env file if it exists
load_dotenv(BASE_DIR / ".env")


class Config:
    """Base application configuration."""

    # Security
    SECRET_KEY = os.environ.get("FLASK_SECRET_KEY", "clouddedup-super-secret-dev-key-change-in-production")

    # Allowed extensions & Upload limits
    ALLOWED_EXTENSIONS = {
        "pdf", "doc", "docx", "txt", "csv", "xls", "xlsx", "jpg", "jpeg", "png", "zip"
    }
    MAX_CONTENT_LENGTH = int(os.environ.get("MAX_CONTENT_LENGTH", 50 * 1024 * 1024))  # Default 50 MB

    # Database Configuration (MySQL XAMPP as primary target)
    MYSQL_HOST = os.environ.get("MYSQL_HOST", "127.0.0.1")
    MYSQL_PORT = int(os.environ.get("MYSQL_PORT", 3306))
    MYSQL_DATABASE = os.environ.get("MYSQL_DATABASE", "clouddedup_db")
    MYSQL_USER = os.environ.get("MYSQL_USER", "root")
    MYSQL_PASSWORD = os.environ.get("MYSQL_PASSWORD", "")

    # Check if explicit database URL is provided
    DATABASE_URL = os.environ.get("DATABASE_URL")
    if DATABASE_URL:
        SQLALCHEMY_DATABASE_URI = DATABASE_URL
    elif os.environ.get("USE_SQLITE", "0") == "1":
        instance_path = BASE_DIR / "instance"
        instance_path.mkdir(parents=True, exist_ok=True)
        db_path = (instance_path / "clouddedup.db").as_posix()
        SQLALCHEMY_DATABASE_URI = f"sqlite:///{db_path}"
    else:
        # Default to MySQL (XAMPP Server)
        SQLALCHEMY_DATABASE_URI = (
            f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}?charset=utf8mb4"
        )

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_recycle": 280,
        "pool_pre_ping": True,
    }

    # Firebase Admin SDK & Cloud Storage Configuration
    FIREBASE_PROJECT_ID = os.environ.get("FIREBASE_PROJECT_ID", "")
    FIREBASE_STORAGE_BUCKET = os.environ.get("FIREBASE_STORAGE_BUCKET", "")
    FIREBASE_SERVICE_ACCOUNT_PATH = os.environ.get(
        "FIREBASE_SERVICE_ACCOUNT_PATH", str(BASE_DIR / "serviceAccountKey.json")
    )

    # Local storage directory (used for buffering uploads before cloud streaming or dev mock)
    LOCAL_STORAGE_DIR = BASE_DIR / "storage_local"


class DevelopmentConfig(Config):
    DEBUG = True


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    WTF_CSRF_ENABLED = False


class ProductionConfig(Config):
    DEBUG = False


config_by_name = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig,
}
