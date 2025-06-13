import pytest
import tempfile
import os
import json
from services.data_service import DataService
from models.child import Child
from models.word import Word


class TestDataService:
    """Test the DataService"""

    @pytest.fixture
    def temp_data_file(self):
        """Create a temporary data file for testing"""
        fd, path = tempfile.mkstemp(suffix=".json")
        os.close(fd)
        yield path
        if os.path.exists(path):
            os.unlink(path)

    @pytest.fixture
    def data_service(self, temp_data_file):
        """Create a DataService instance with temporary file"""
        service = DataService()
        service.data_file = temp_data_file
        service._ensure_data_file_exists()
        return service

    def test_ensure_data_file_exists(self, temp_data_file):
        # Remove the file first
        if os.path.exists(temp_data_file):
            os.unlink(temp_data_file)

        service = DataService()
        service.data_file = temp_data_file
        service._ensure_data_file_exists()

        assert os.path.exists(temp_data_file)

        # Check file contents
        with open(temp_data_file, "r") as f:
            data = json.load(f)
        assert data == {"children": []}

    def test_load_empty_data(self, data_service):
        data = data_service.load_data()
        assert data == {"children": []}

    def test_save_and_load_data(self, data_service):
        test_data = {
            "children": [
                {"name": "Alice", "words": []},
                {"name": "Bob", "words": []}
            ]
        }

        data_service.save_data(test_data)
        loaded_data = data_service.load_data()

        assert loaded_data == test_data

    def test_get_children_empty(self, data_service):
        children = data_service.get_children()
        assert children == []

    def test_save_and_get_child(self, data_service):
        child = Child("Charlie")
        data_service.save_child(child)

        children = data_service.get_children()
        assert len(children) == 1
        assert children[0].name == "Charlie"

    def test_get_specific_child(self, data_service):
        child1 = Child("Dana")
        child2 = Child("Eve")

        data_service.save_child(child1)
        data_service.save_child(child2)

        found_child = data_service.get_child("Dana")
        assert found_child is not None
        assert found_child.name == "Dana"

        not_found = data_service.get_child("Frank")
        assert not_found is None

    def test_update_existing_child(self, data_service):
        # Save initial child
        child = Child("Grace")
        word = Word("hello")
        child.add_word(word)
        data_service.save_child(child)

        # Update child with new word
        updated_child = Child("Grace")
        word1 = Word("hello")
        word2 = Word("world")
        updated_child.add_word(word1)
        updated_child.add_word(word2)
        data_service.save_child(updated_child)

        # Verify update
        retrieved_child = data_service.get_child("Grace")
        assert len(retrieved_child.words) == 2

    def test_delete_child(self, data_service):
        child1 = Child("Henry")
        child2 = Child("Ivy")

        data_service.save_child(child1)
        data_service.save_child(child2)

        assert len(data_service.get_children()) == 2

        deleted = data_service.delete_child("Henry")
        assert deleted is True

        children = data_service.get_children()
        assert len(children) == 1
        assert children[0].name == "Ivy"

        # Try to delete non-existent child
        not_deleted = data_service.delete_child("Jack")
        assert not_deleted is False

    def test_add_word_to_child(self, data_service):
        child = Child("Kate")
        data_service.save_child(child)

        word = Word("mama")
        success = data_service.add_word_to_child("Kate", word)
        assert success is True

        retrieved_child = data_service.get_child("Kate")
        assert len(retrieved_child.words) == 1
        assert retrieved_child.words[0].text == "mama"

        # Try with non-existent child
        failure = data_service.add_word_to_child("Leo", Word("papa"))
        assert failure is False

    def test_add_recording_to_word(self, data_service):
        child = Child("Maya")
        word = Word("water")
        child.add_word(word)
        data_service.save_child(child)

        success = data_service.add_recording_to_word(
            "Maya", "water", 2023, "water_2023.mp3"
        )
        assert success is True

        retrieved_child = data_service.get_child("Maya")
        retrieved_word = retrieved_child.get_word("water")
        assert len(retrieved_word.recordings) == 1
        assert retrieved_word.recordings[0].year == 2023
        assert retrieved_word.recordings[0].filename == "water_2023.mp3"

        # Try with non-existent child
        failure = data_service.add_recording_to_word(
            "Noah", "water", 2023, "test.mp3"
        )
        assert failure is False

        # Try with non-existent word
        failure = data_service.add_recording_to_word(
            "Maya", "juice", 2023, "test.mp3"
        )
        assert failure is False
