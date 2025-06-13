import os
import tomllib
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()


def get_project_version() -> str:
    """Get version from pyproject.toml"""
    try:
        pyproject_path = Path(__file__).parent / "pyproject.toml"
        with open(pyproject_path, "rb") as f:
            pyproject_data = tomllib.load(f)
        return pyproject_data.get("project", {}).get("version", "unknown")
    except Exception:
        return "unknown"


class Config:
    """Base configuration"""

    SECRET_KEY = os.environ.get("SECRET_KEY") or "dev-secret-key-change-in-production"
    DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
    AUDIO_DIR = os.path.join(DATA_DIR, "audio")
    IMAGES_DIR = os.path.join(DATA_DIR, "images")
    DATA_FILE = os.path.join(DATA_DIR, "data.json")

    ALLOWED_AUDIO_EXTENSIONS = {"mp3", "wav", "ogg", "m4a", "webm"}
    ALLOWED_IMAGE_EXTENSIONS = {"jpg", "jpeg", "png", "gif"}

    MAX_AUDIO_SIZE = 10 * 1024 * 1024  # 10MB
    MAX_IMAGE_SIZE = 5 * 1024 * 1024  # 5MB

    # Image search API configuration
    # Using Pixabay API (free, no authentication required for basic usage)
    IMAGE_SEARCH_API_URL = "https://pixabay.com/api/"
    IMAGE_SEARCH_API_KEY = os.environ.get(
        "PIXABAY_API_KEY", ""
    )  # Optional, can work without key but with limits
    IMAGE_SEARCH_RESULTS_PER_PAGE = 20
    IMAGE_SEARCH_SAFESEARCH = "true"  # Enable safe search for child-friendly content

    @staticmethod
    def init_app(app):
        os.makedirs(Config.DATA_DIR, exist_ok=True)
        os.makedirs(Config.AUDIO_DIR, exist_ok=True)
        os.makedirs(Config.IMAGES_DIR, exist_ok=True)


class DevelopmentConfig(Config):
    """Development configuration"""

    DEBUG = True


class ProductionConfig(Config):
    """Production configuration"""

    DEBUG = False
    TESTING = False

    # Use environment variables for production settings
    SECRET_KEY = os.environ.get("SECRET_KEY") or "change-this-in-production-please"

    # Database/Storage paths - use mounted volumes in production
    DATA_DIR = os.environ.get("DATA_DIR") or "/app/data"
    AUDIO_DIR = os.path.join(DATA_DIR, "audio")
    IMAGES_DIR = os.path.join(DATA_DIR, "images")
    DATA_FILE = os.path.join(DATA_DIR, "data.json")

    # File size limits (can be overridden by environment)
    MAX_AUDIO_SIZE = int(os.environ.get("MAX_AUDIO_SIZE", 20 * 1024 * 1024))  # 20MB default
    MAX_IMAGE_SIZE = int(os.environ.get("MAX_IMAGE_SIZE", 10 * 1024 * 1024))  # 10MB default

    @staticmethod
    def init_app(app):
        Config.init_app(app)

        # Log to stderr in production
        import logging
        from logging import StreamHandler

        # Set up logging
        if not app.debug:
            stream_handler = StreamHandler()
            stream_handler.setLevel(logging.INFO)
            app.logger.addHandler(stream_handler)
            app.logger.setLevel(logging.INFO)
            app.logger.info("Paraulins startup")


class TestingConfig(Config):
    """Testing configuration"""

    TESTING = True
    WTF_CSRF_ENABLED = False


# Configuration dictionary
config = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig,
}
