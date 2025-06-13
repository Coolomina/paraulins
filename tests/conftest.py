import pytest
import tempfile
import os
from app import create_app
from config import Config


class TestConfig(Config):
    TESTING = True
    DATA_DIR = tempfile.mkdtemp()
    AUDIO_DIR = os.path.join(DATA_DIR, "audio")
    IMAGES_DIR = os.path.join(DATA_DIR, "images")
    DATA_FILE = os.path.join(DATA_DIR, "data.json")


@pytest.fixture
def app():
    """Create and configure a new app instance for each test."""
    app = create_app()
    app.config.from_object(TestConfig)

    with app.app_context():
        TestConfig.init_app(app)
        yield app


@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()


@pytest.fixture
def runner(app):
    """A test runner for the app's Click commands."""
    return app.test_cli_runner()
