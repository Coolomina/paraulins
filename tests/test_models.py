from models.child import Child
from models.recording import Recording
from models.word import Word


class TestChild:
    """Test the Child model"""

    def test_child_creation(self):
        child = Child("Alice")
        assert child.name == "Alice"
        assert child.words == []

    def test_child_with_words(self):
        words = [Word("hello"), Word("world")]
        child = Child("Bob", words)
        assert child.name == "Bob"
        assert len(child.words) == 2
        assert child.words[0].text == "hello"
        assert child.words[1].text == "world"

    def test_add_word(self):
        child = Child("Charlie")
        word = Word("mama")
        child.add_word(word)

        assert len(child.words) == 1
        assert child.words[0].text == "mama"

    def test_add_duplicate_word(self):
        child = Child("Dana")
        word1 = Word("papa")
        word2 = Word("papa")

        child.add_word(word1)
        child.add_word(word2)  # Should not add duplicate

        assert len(child.words) == 1

    def test_get_word(self):
        child = Child("Eve")
        word = Word("water")
        child.add_word(word)

        found_word = child.get_word("water")
        assert found_word is not None
        assert found_word.text == "water"

        not_found = child.get_word("juice")
        assert not_found is None

    def test_remove_word(self):
        child = Child("Frank")
        word = Word("book")
        child.add_word(word)

        assert len(child.words) == 1

        removed = child.remove_word("book")
        assert removed is True
        assert len(child.words) == 0

        not_removed = child.remove_word("book")
        assert not_removed is False

    def test_to_dict(self):
        child = Child("Grace")
        word = Word("cat")
        word.add_recording(2023, 6, 15, "cat_2023.mp3")
        child.add_word(word)

        data = child.to_dict()

        assert data["name"] == "Grace"
        assert len(data["words"]) == 1
        assert data["words"][0]["text"] == "cat"
        assert len(data["words"][0]["recordings"]) == 1

    def test_from_dict(self):
        data = {
            "name": "Henry",
            "words": [
                {
                    "text": "dog",
                    "image_filename": "dog.jpg",
                    "recordings": [
                        {"year": 2022, "filename": "dog_2022.mp3"},
                        {"year": 2023, "filename": "dog_2023.mp3"},
                    ],
                }
            ],
        }

        child = Child.from_dict(data)

        assert child.name == "Henry"
        assert len(child.words) == 1
        assert child.words[0].text == "dog"
        assert child.words[0].image_filename == "dog.jpg"
        assert len(child.words[0].recordings) == 2


class TestWord:
    """Test the Word model"""

    def test_word_creation(self):
        word = Word("hello")
        assert word.text == "hello"
        assert word.image_filename is None
        assert word.recordings == []

    def test_word_with_image(self):
        word = Word("world", "world.jpg")
        assert word.text == "world"
        assert word.image_filename == "world.jpg"

    def test_add_recording(self):
        word = Word("mama")
        word.add_recording(2023, 6, 15, "mama_2023.mp3")

        assert len(word.recordings) == 1
        assert word.recordings[0].year == 2023
        assert word.recordings[0].month == 6
        assert word.recordings[0].day == 15
        assert word.recordings[0].filename == "mama_2023.mp3"

    def test_add_multiple_recordings(self):
        word = Word("papa")
        word.add_recording(2022, 3, 10, "papa_2022.mp3")
        word.add_recording(2023, 6, 15, "papa_2023.mp3")
        word.add_recording(2021, 12, 25, "papa_2021.mp3")

        assert len(word.recordings) == 3
        # Should be sorted by year, month, day
        years = [r.year for r in word.recordings]
        assert years == [2021, 2022, 2023]

    def test_replace_recording(self):
        word = Word("water")
        word.add_recording(2023, 6, 15, "water_2023_v1.mp3")
        word.add_recording(2023, 6, 15, "water_2023_v2.mp3")  # Same date, should replace

        assert len(word.recordings) == 1
        assert word.recordings[0].filename == "water_2023_v2.mp3"

    def test_get_recording(self):
        word = Word("book")
        word.add_recording(2022, 3, 10, "book_2022.mp3")
        word.add_recording(2023, 6, 15, "book_2023.mp3")

        recording = word.get_recording(2022, 3, 10)
        assert recording is not None
        assert recording.year == 2022
        assert recording.month == 3
        assert recording.day == 10
        assert recording.filename == "book_2022.mp3"

        not_found = word.get_recording(2024, 1, 1)
        assert not_found is None

    def test_remove_recording(self):
        word = Word("cat")
        word.add_recording(2023, 6, 15, "cat_2023.mp3")

        assert len(word.recordings) == 1

        removed = word.remove_recording(2023, 6, 15)
        assert removed is True
        assert len(word.recordings) == 0

        not_removed = word.remove_recording(2023, 6, 15)
        assert not_removed is False

    def test_get_years(self):
        word = Word("dog")
        word.add_recording(2023, 6, 15, "dog_2023.mp3")
        word.add_recording(2021, 3, 10, "dog_2021.mp3")
        word.add_recording(2022, 12, 25, "dog_2022.mp3")

        years = word.get_years()
        assert years == [2021, 2022, 2023]

    def test_set_image(self):
        word = Word("bird")
        word.set_image("bird.png")

        assert word.image_filename == "bird.png"

    def test_to_dict(self):
        word = Word("fish", "fish.jpg")
        word.add_recording(2022, 3, 10, "fish_2022.mp3")
        word.add_recording(2023, 6, 15, "fish_2023.mp3")

        data = word.to_dict()

        assert data["text"] == "fish"
        assert data["image_filename"] == "fish.jpg"
        assert len(data["recordings"]) == 2
        assert data["recordings"][0]["year"] == 2022
        assert data["recordings"][1]["year"] == 2023

    def test_from_dict(self):
        data = {
            "text": "tree",
            "image_filename": "tree.png",
            "recordings": [
                {"year": 2021, "filename": "tree_2021.mp3"},
                {"year": 2022, "filename": "tree_2022.mp3"},
            ],
        }

        word = Word.from_dict(data)

        assert word.text == "tree"
        assert word.image_filename == "tree.png"
        assert len(word.recordings) == 2
        assert word.recordings[0].year == 2021
        assert word.recordings[1].year == 2022


class TestRecording:
    """Test the Recording model"""

    def test_recording_creation(self):
        recording = Recording(2023, 6, 15, "hello_2023.mp3")
        assert recording.year == 2023
        assert recording.month == 6
        assert recording.day == 15
        assert recording.filename == "hello_2023.mp3"

    def test_to_dict(self):
        recording = Recording(2022, 3, 10, "world_2022.wav")
        data = recording.to_dict()

        assert data["year"] == 2022
        assert data["month"] == 3
        assert data["day"] == 10
        assert data["filename"] == "world_2022.wav"

    def test_from_dict(self):
        data = {"year": 2021, "filename": "test_2021.ogg"}
        recording = Recording.from_dict(data)

        assert recording.year == 2021
        assert recording.filename == "test_2021.ogg"
