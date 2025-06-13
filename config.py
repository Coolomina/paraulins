import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    SECRET_KEY = (
        os.environ.get("SECRET_KEY") or "dev-secret-key-change-in-production"
    )
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
