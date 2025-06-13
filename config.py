import os

from dotenv import load_dotenv

load_dotenv()


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
            app.logger.info("Family Voices startup")


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
