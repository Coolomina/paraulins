import os
import shutil
import tempfile

import pytest

from app import create_app
from config import Config
from models.child import Child
from models.word import Word
from services.data_service import DataService


class TestConfig(Config):
    TESTING = True
    DATA_DIR = None  # Will be set in init_app
    AUDIO_DIR = None  # Will be set in init_app
    IMAGES_DIR = None  # Will be set in init_app
    DATA_FILE = None  # Will be set in init_app

    @staticmethod
    def init_app(app):
        """Initialize test configuration with temporary directories"""
        TestConfig.DATA_DIR = tempfile.mkdtemp()
        TestConfig.AUDIO_DIR = os.path.join(TestConfig.DATA_DIR, "audio")
        TestConfig.IMAGES_DIR = os.path.join(TestConfig.DATA_DIR, "images")
        TestConfig.DATA_FILE = os.path.join(TestConfig.DATA_DIR, "data.json")

        # Update app config with the new paths
        app.config["DATA_DIR"] = TestConfig.DATA_DIR
        app.config["AUDIO_DIR"] = TestConfig.AUDIO_DIR
        app.config["IMAGES_DIR"] = TestConfig.IMAGES_DIR
        app.config["DATA_FILE"] = TestConfig.DATA_FILE

        # Create directories
        os.makedirs(TestConfig.DATA_DIR, exist_ok=True)
        os.makedirs(TestConfig.AUDIO_DIR, exist_ok=True)
        os.makedirs(TestConfig.IMAGES_DIR, exist_ok=True)


@pytest.fixture
def app():
    """Create and configure a new app instance for each test."""
    app = create_app()
    app.config.from_object(TestConfig)

    with app.app_context():
        TestConfig.init_app(app)
        yield app

    # Clean up the temporary directory after the test
    if (
        hasattr(TestConfig, "DATA_DIR")
        and TestConfig.DATA_DIR
        and os.path.exists(TestConfig.DATA_DIR)
    ):
        shutil.rmtree(TestConfig.DATA_DIR)


@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()


@pytest.fixture
def runner(app):
    """A test runner for the app's Click commands."""
    return app.test_cli_runner()


@pytest.fixture
def clean_data_service(app):
    """A clean data service with no existing data."""
    with app.app_context():
        data_service = DataService()
        # Ensure clean state - create empty data file
        data_service._ensure_data_file_exists()
        yield data_service


@pytest.fixture
def sample_child(clean_data_service):
    """A sample child with some words and recordings for testing."""
    child = Child("TestChild")

    # Add a word with recording
    word1 = Word("hello")
    word1.add_recording(2023, 6, 15, "hello_2023-06-15.mp3")
    child.add_word(word1)

    # Add a word without recording
    word2 = Word("world")
    child.add_word(word2)

    clean_data_service.save_child(child)
    yield child
