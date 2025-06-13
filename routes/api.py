from flask import Blueprint, jsonify, request, send_file
from services.data_service import DataService
from services.audio_service import AudioService
from services.image_service import ImageService
from models.child import Child
from models.word import Word

api = Blueprint("api", __name__)


@api.route("/children", methods=["GET"])
def get_children():
    """Get all children"""
    try:
        data_service = DataService()
        children = data_service.get_children()
        return jsonify([child.to_dict() for child in children])
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@api.route("/children", methods=["POST"])
def create_child():
    """Create a new child"""
    try:
        data = request.get_json()
        if not data or "name" not in data:
            return jsonify({"error": "Child name is required"}), 400

        name = data["name"].strip()
        if not name:
            return jsonify({"error": "Child name cannot be empty"}), 400

        data_service = DataService()
        # Check if child already exists
        if data_service.get_child(name):
            return jsonify({"error": "Child already exists"}), 409

        child = Child(name)
        data_service.save_child(child)

        return jsonify(child.to_dict()), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@api.route("/children/<child_name>", methods=["GET"])
def get_child(child_name):
    """Get a specific child"""
    try:
        data_service = DataService()
        child = data_service.get_child(child_name)
        if not child:
            return jsonify({"error": "Child not found"}), 404

        return jsonify(child.to_dict())
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@api.route("/children/<child_name>/words", methods=["POST"])
def add_word_to_child(child_name):
    """Add a word to a child's vocabulary"""
    try:
        data_service = DataService()
        child = data_service.get_child(child_name)
        if not child:
            return jsonify({"error": "Child not found"}), 404

        data = request.get_json()
        if not data or "text" not in data:
            return jsonify({"error": "Word text is required"}), 400

        word_text = data["text"].strip()
        if not word_text:
            return jsonify({"error": "Word text cannot be empty"}), 400

        # Check if word already exists
        if child.get_word(word_text):
            return jsonify({
                "error": "Word already exists for this child"
            }), 409

        word = Word(word_text)
        child.add_word(word)
        data_service.save_child(child)

        return jsonify(word.to_dict()), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@api.route("/children/<child_name>/words/<word_text>/image", methods=["POST"])
def upload_word_image(child_name, word_text):
    """Upload an image for a word"""
    try:
        data_service = DataService()
        child = data_service.get_child(child_name)
        if not child:
            return jsonify({"error": "Child not found"}), 404

        word = child.get_word(word_text)
        if not word:
            return jsonify({"error": "Word not found"}), 404

        if "image" not in request.files:
            return jsonify({"error": "No image file provided"}), 400

        file = request.files["image"]
        if file.filename == "":
            return jsonify({"error": "No image file selected"}), 400

        image_service = ImageService()
        filename = image_service.save_image_file(file, word_text)
        if filename:
            word.set_image(filename)
            data_service.save_child(child)
            return jsonify({"filename": filename})
        else:
            return jsonify({"error": "Failed to save image"}), 500

    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@api.route(
    "/children/<child_name>/words/<word_text>/recordings", methods=["POST"]
)
def upload_recording(child_name, word_text):
    """Upload an audio recording for a word"""
    try:
        data_service = DataService()
        child = data_service.get_child(child_name)
        if not child:
            return jsonify({"error": "Child not found"}), 404

        word = child.get_word(word_text)
        if not word:
            return jsonify({"error": "Word not found"}), 404

        if "audio" not in request.files:
            return jsonify({"error": "No audio file provided"}), 400

        file = request.files["audio"]
        if file.filename == "":
            return jsonify({"error": "No audio file selected"}), 400

        if "year" not in request.form:
            return jsonify({"error": "Year is required"}), 400

        if "month" not in request.form:
            return jsonify({"error": "Month is required"}), 400

        try:
            year = int(request.form["year"])
            month = int(request.form["month"])
        except ValueError:
            return jsonify({"error": "Year and month must be valid integers"}), 400

        if not (1 <= month <= 12):
            return jsonify({"error": "Month must be between 1 and 12"}), 400

        audio_service = AudioService()
        filename = audio_service.save_audio_file(
            file, child_name, word_text, year, month
        )
        if filename:
            word.add_recording(year, month, filename)
            data_service.save_child(child)
            return jsonify({"year": year, "month": month, "filename": filename})
        else:
            return jsonify({"error": "Failed to save audio"}), 500

    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@api.route("/audio/<child_name>/<word_text>/<filename>")
def serve_audio(child_name, word_text, filename):
    """Serve an audio file"""
    try:
        audio_service = AudioService()
        file_path = audio_service.get_audio_file_path(
            child_name, word_text, filename
        )
        if not file_path:
            return jsonify({"error": "Audio file not found"}), 404

        return send_file(file_path)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@api.route("/images/<filename>")
def serve_image(filename):
    """Serve an image file"""
    try:
        image_service = ImageService()
        file_path = image_service.get_image_file_path(filename)
        if not file_path:
            return jsonify({"error": "Image file not found"}), 404

        return send_file(file_path)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@api.route(
    "/children/<child_name>/words/<word_text>/recordings/<int:year>/<int:month>",
    methods=["DELETE"]
)
def delete_recording(child_name, word_text, year, month):
    """Delete a recording for a specific month and year"""
    try:
        if not (1 <= month <= 12):
            return jsonify({"error": "Month must be between 1 and 12"}), 400

        data_service = DataService()
        child = data_service.get_child(child_name)
        if not child:
            return jsonify({"error": "Child not found"}), 404

        word = child.get_word(word_text)
        if not word:
            return jsonify({"error": "Word not found"}), 404

        recording = word.get_recording(year, month)
        if not recording:
            return jsonify({"error": "Recording not found"}), 404

        # Delete the audio file
        audio_service = AudioService()
        audio_service.delete_audio_file(
            child_name, word_text, recording.filename
        )

        # Remove from word
        word.remove_recording(year, month)
        data_service.save_child(child)

        return jsonify({"message": "Recording deleted successfully"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Legacy route for backward compatibility (year only)
@api.route(
    "/children/<child_name>/words/<word_text>/recordings/<int:year>",
    methods=["DELETE"]
)
def delete_recording_legacy(child_name, word_text, year):
    """Delete a recording for a specific year (legacy - deletes first recording of that year)"""
    try:
        data_service = DataService()
        child = data_service.get_child(child_name)
        if not child:
            return jsonify({"error": "Child not found"}), 404

        word = child.get_word(word_text)
        if not word:
            return jsonify({"error": "Word not found"}), 404

        # Find first recording for this year
        year_recordings = [r for r in word.recordings if r.year == year]
        if not year_recordings:
            return jsonify({"error": "Recording not found"}), 404

        recording = year_recordings[0]

        # Delete the audio file
        audio_service = AudioService()
        audio_service.delete_audio_file(
            child_name, word_text, recording.filename
        )

        # Remove from word
        word.remove_recording(recording.year, recording.month)
        data_service.save_child(child)

        return jsonify({"message": "Recording deleted successfully"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
