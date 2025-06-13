import os

from models.child import Child
from models.word import Word


class TestDataService:
    """Test the DataService class"""

    def test_ensure_data_file_exists(self, clean_data_service):
        """Test that data file is created if it doesn't exist"""
        # The fixture should have already created the file
        assert os.path.exists(clean_data_service.data_file)

    def test_load_empty_data(self, clean_data_service):
        """Test loading data from empty file"""
        children = clean_data_service.get_children()
        assert children == []

    def test_save_and_load_data(self, clean_data_service):
        """Test saving and loading data"""
        child = Child("Test Child")
        clean_data_service.save_child(child)

        # Load data and verify
        children = clean_data_service.get_children()
        assert len(children) == 1
        assert children[0].name == "Test Child"

    def test_get_children_empty(self, clean_data_service):
        """Test getting children when none exist"""
        children = clean_data_service.get_children()
        assert children == []

    def test_save_and_get_child(self, clean_data_service):
        """Test saving and retrieving a specific child"""
        child = Child("Alice")
        clean_data_service.save_child(child)

        retrieved = clean_data_service.get_child("Alice")
        assert retrieved is not None
        assert retrieved.name == "Alice"

        # Test non-existent child
        not_found = clean_data_service.get_child("Bob")
        assert not_found is None

    def test_get_specific_child(self, sample_child, clean_data_service):
        """Test getting a specific child with sample data"""
        retrieved = clean_data_service.get_child("TestChild")
        assert retrieved is not None
        assert retrieved.name == "TestChild"
        assert len(retrieved.words) == 2

    def test_update_existing_child(self, clean_data_service):
        """Test updating an existing child"""
        # Create initial child
        child = Child("Charlie")
        clean_data_service.save_child(child)

        # Add a word and save again
        word = Word("test")
        child.add_word(word)
        clean_data_service.save_child(child)

        # Verify update
        retrieved = clean_data_service.get_child("Charlie")
        assert len(retrieved.words) == 1
        assert retrieved.words[0].text == "test"

    def test_delete_child(self, clean_data_service):
        """Test deleting a child"""
        # Create child
        child = Child("Dana")
        clean_data_service.save_child(child)

        # Verify it exists
        assert clean_data_service.get_child("Dana") is not None

        # Delete it
        deleted = clean_data_service.delete_child("Dana")
        assert deleted is True

        # Verify it's gone
        assert clean_data_service.get_child("Dana") is None

        # Try to delete non-existent child
        not_deleted = clean_data_service.delete_child("NonExistent")
        assert not_deleted is False

    def test_add_word_to_child(self, clean_data_service):
        """Test adding a word to a child through the service"""
        child = Child("Eve")
        clean_data_service.save_child(child)

        word = Word("hello")
        success = clean_data_service.add_word_to_child("Eve", word)
        assert success is True

        retrieved = clean_data_service.get_child("Eve")
        assert len(retrieved.words) == 1
        assert retrieved.words[0].text == "hello"

        # Try with non-existent child
        word2 = Word("word")
        failure = clean_data_service.add_word_to_child("NonExistent", word2)
        assert failure is False

    def test_add_recording_to_word(self, clean_data_service):
        """Test adding a recording to a word through the service"""
        child = Child("Maya")
        word = Word("water")
        child.add_word(word)
        clean_data_service.save_child(child)

        success = clean_data_service.add_recording_to_word(
            "Maya", "water", 2023, 6, 15, "water_2023.mp3"
        )
        assert success is True

        retrieved_child = clean_data_service.get_child("Maya")
        retrieved_word = retrieved_child.get_word("water")
        assert len(retrieved_word.recordings) == 1
        assert retrieved_word.recordings[0].year == 2023
        assert retrieved_word.recordings[0].month == 6
        assert retrieved_word.recordings[0].day == 15
        assert retrieved_word.recordings[0].filename == "water_2023.mp3"

        # Try with non-existent child
        failure = clean_data_service.add_recording_to_word("Noah", "water", 2023, 6, 15, "test.mp3")
        assert failure is False

        # Try with non-existent word
        failure = clean_data_service.add_recording_to_word("Maya", "juice", 2023, 6, 15, "test.mp3")
        assert failure is False
