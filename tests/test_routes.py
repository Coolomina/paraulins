import json
import io
from unittest.mock import patch, MagicMock


class TestAPI:
    """Test the API routes"""

    def test_get_children_empty(self, client):
        """Test getting children when none exist"""
        response = client.get("/api/children")
        assert response.status_code == 200

        data = json.loads(response.data)
        assert data == []

    def test_create_child(self, client):
        """Test creating a new child"""
        response = client.post(
            "/api/children",
            json={"name": "Alice"},
            content_type="application/json"
        )

        assert response.status_code == 201

        data = json.loads(response.data)
        assert data["name"] == "Alice"
        assert data["words"] == []

    def test_create_child_missing_name(self, client):
        """Test creating child without name"""
        response = client.post(
            "/api/children", json={}, content_type="application/json"
        )

        assert response.status_code == 400

        data = json.loads(response.data)
        assert "error" in data

    def test_create_child_empty_name(self, client):
        """Test creating child with empty name"""
        response = client.post(
            "/api/children",
            json={"name": "   "},
            content_type="application/json"
        )

        assert response.status_code == 400

        data = json.loads(response.data)
        assert "error" in data

    def test_create_duplicate_child(self, client):
        """Test creating duplicate child"""
        # Create first child
        client.post(
            "/api/children",
            json={"name": "Bob"},
            content_type="application/json"
        )

        # Try to create duplicate
        response = client.post(
            "/api/children",
            json={"name": "Bob"},
            content_type="application/json"
        )

        assert response.status_code == 409

        data = json.loads(response.data)
        assert "error" in data

    def test_get_specific_child(self, client):
        """Test getting a specific child"""
        # Create a child first
        client.post("/api/children", json={"name": "Charlie"}, content_type="application/json")

        response = client.get("/api/children/Charlie")
        assert response.status_code == 200

        data = json.loads(response.data)
        assert data["name"] == "Charlie"

    def test_get_nonexistent_child(self, client):
        """Test getting a child that doesn't exist"""
        response = client.get("/api/children/Nonexistent")
        assert response.status_code == 404

        data = json.loads(response.data)
        assert "error" in data

    def test_add_word_to_child(self, client):
        """Test adding a word to a child"""
        # Create a child first
        client.post("/api/children", json={"name": "Dana"}, content_type="application/json")

        response = client.post(
            "/api/children/Dana/words", json={"text": "hello"}, content_type="application/json"
        )

        assert response.status_code == 201

        data = json.loads(response.data)
        assert data["text"] == "hello"
        assert data["recordings"] == []

    def test_add_word_missing_text(self, client):
        """Test adding word without text"""
        client.post("/api/children", json={"name": "Eve"}, content_type="application/json")

        response = client.post("/api/children/Eve/words", json={}, content_type="application/json")

        assert response.status_code == 400

    def test_add_word_to_nonexistent_child(self, client):
        """Test adding word to non-existent child"""
        response = client.post(
            "/api/children/Nonexistent/words",
            json={"text": "hello"},
            content_type="application/json",
        )

        assert response.status_code == 404

    def test_add_duplicate_word(self, client):
        """Test adding duplicate word to child"""
        # Create child and add word
        client.post("/api/children", json={"name": "Frank"}, content_type="application/json")

        client.post(
            "/api/children/Frank/words", json={"text": "mama"}, content_type="application/json"
        )

        # Try to add same word again
        response = client.post(
            "/api/children/Frank/words", json={"text": "mama"}, content_type="application/json"
        )

        assert response.status_code == 409

    def test_upload_word_image(self, client):
        """Test uploading an image for a word"""
        # Create child and word
        client.post("/api/children", json={"name": "Grace"}, content_type="application/json")

        client.post(
            "/api/children/Grace/words", json={"text": "cat"}, content_type="application/json"
        )

        # Create a fake image file
        data = {"image": (io.BytesIO(b"fake image data"), "test.jpg")}

        with patch("services.image_service.ImageService.save_image_file") as mock_save:
            mock_save.return_value = "cat.jpg"

            response = client.post(
                "/api/children/Grace/words/cat/image", data=data, content_type="multipart/form-data"
            )

            assert response.status_code == 200

            data = json.loads(response.data)
            assert data["filename"] == "cat.jpg"

    def test_upload_recording(self, client):
        """Test uploading an audio recording"""
        # Create child and word
        client.post("/api/children", json={"name": "Henry"}, content_type="application/json")

        client.post(
            "/api/children/Henry/words", json={"text": "dog"}, content_type="application/json"
        )

        # Create a fake audio file
        data = {"audio": (io.BytesIO(b"fake audio data"), "test.mp3"), "year": "2023"}

        with patch("services.audio_service.AudioService.save_audio_file") as mock_save:
            mock_save.return_value = "2023.mp3"

            response = client.post(
                "/api/children/Henry/words/dog/recordings",
                data=data,
                content_type="multipart/form-data",
            )

            assert response.status_code == 200

            response_data = json.loads(response.data)
            assert response_data["year"] == 2023
            assert response_data["filename"] == "2023.mp3"

    def test_upload_recording_missing_year(self, client):
        """Test uploading recording without year"""
        # Create child and word
        client.post("/api/children", json={"name": "Ivy"}, content_type="application/json")

        client.post(
            "/api/children/Ivy/words", json={"text": "bird"}, content_type="application/json"
        )

        # Create a fake audio file without year
        data = {"audio": (io.BytesIO(b"fake audio data"), "test.mp3")}

        response = client.post(
            "/api/children/Ivy/words/bird/recordings", data=data, content_type="multipart/form-data"
        )

        assert response.status_code == 400

    def test_upload_recording_invalid_year(self, client):
        """Test uploading recording with invalid year"""
        # Create child and word
        client.post("/api/children", json={"name": "Jack"}, content_type="application/json")

        client.post(
            "/api/children/Jack/words", json={"text": "fish"}, content_type="application/json"
        )

        # Create a fake audio file with invalid year
        data = {"audio": (io.BytesIO(b"fake audio data"), "test.mp3"), "year": "not_a_year"}

        response = client.post(
            "/api/children/Jack/words/fish/recordings",
            data=data,
            content_type="multipart/form-data",
        )

        assert response.status_code == 400

    def test_serve_audio_file(self, client):
        """Test serving an audio file"""
        with patch("services.audio_service.AudioService.get_audio_file_path") as mock_get_path:
            mock_get_path.return_value = "/fake/path/to/audio.mp3"

            with patch("routes.api.send_file") as mock_send_file:
                mock_send_file.return_value = MagicMock()

                client.get("/api/audio/TestChild/testword/test.mp3")

                mock_get_path.assert_called_once_with("TestChild", "testword", "test.mp3")
                mock_send_file.assert_called_once_with("/fake/path/to/audio.mp3")

    def test_serve_nonexistent_audio_file(self, client):
        """Test serving a non-existent audio file"""
        with patch("services.audio_service.AudioService.get_audio_file_path") as mock_get_path:
            mock_get_path.return_value = None

            response = client.get("/api/audio/TestChild/testword/nonexistent.mp3")
            assert response.status_code == 404

    def test_serve_image_file(self, client):
        """Test serving an image file"""
        with patch("services.image_service.ImageService.get_image_file_path") as mock_get_path:
            mock_get_path.return_value = "/fake/path/to/image.jpg"

            with patch("routes.api.send_file") as mock_send_file:
                mock_send_file.return_value = MagicMock()

                client.get("/api/images/test.jpg")

                mock_get_path.assert_called_once_with("test.jpg")
                mock_send_file.assert_called_once_with("/fake/path/to/image.jpg")

    def test_serve_nonexistent_image_file(self, client):
        """Test serving a non-existent image file"""
        with patch("services.image_service.ImageService.get_image_file_path") as mock_get_path:
            mock_get_path.return_value = None

            response = client.get("/api/images/nonexistent.jpg")
            assert response.status_code == 404

    def test_delete_recording(self, client):
        """Test deleting a recording"""
        # Create child, word, and recording
        client.post("/api/children", json={"name": "Luna"}, content_type="application/json")

        client.post(
            "/api/children/Luna/words", json={"text": "moon"}, content_type="application/json"
        )

        # Mock adding a recording
        data = {"audio": (io.BytesIO(b"fake audio data"), "test.mp3"), "year": "2023"}

        with patch("services.audio_service.AudioService.save_audio_file") as mock_save:
            mock_save.return_value = "2023.mp3"

            client.post(
                "/api/children/Luna/words/moon/recordings",
                data=data,
                content_type="multipart/form-data",
            )

        # Now delete the recording
        with patch("services.audio_service.AudioService.delete_audio_file") as mock_delete:
            mock_delete.return_value = True

            response = client.delete("/api/children/Luna/words/moon/recordings/2023")
            assert response.status_code == 200

            response_data = json.loads(response.data)
            assert "message" in response_data


class TestWebRoutes:
    """Test the web routes"""

    def test_index_page(self, client):
        """Test the main index page"""
        response = client.get("/")
        assert response.status_code == 200
        assert b"Family Voices" in response.data

    def test_child_page(self, client):
        """Test the child-specific page"""
        # Create a child first
        client.post("/api/children", json={"name": "TestChild"}, content_type="application/json")

        response = client.get("/child/TestChild")
        assert response.status_code == 200
        assert b"TestChild" in response.data

    def test_child_page_not_found(self, client):
        """Test child page for non-existent child"""
        response = client.get("/child/NonexistentChild")
        assert response.status_code == 404
        assert b"Child not found" in response.data
