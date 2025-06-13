from flask import Blueprint, jsonify, request, send_file

from config import get_project_version
from models.child import Child
from models.word import Word
from services.audio_service import AudioService
from services.data_service import DataService
from services.image_search_service import ImageSearchService
from services.image_service import ImageService

api = Blueprint("api", __name__)


@api.route("/health", methods=["GET"])
def health_check():
    """Health check endpoint for container monitoring"""
    try:
        # Basic health check - verify services can be instantiated
        data_service = DataService()
        # Simple validation that services are working
        children = data_service.get_children()
        return (
            jsonify(
                {
                    "status": "healthy",
                    "service": "paraulins",
                    "version": get_project_version(),
                    "children_count": len(children),
                }
            ),
            200,
        )
    except Exception as e:
        return jsonify({"status": "unhealthy", "error": str(e)}), 503


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
            return jsonify({"error": "Word already exists for this child"}), 409

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


@api.route("/children/<child_name>/words/<word_text>/recordings", methods=["POST"])
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

        if "date" not in request.form:
            return jsonify({"error": "Date is required"}), 400

        try:
            # Parse date string (YYYY-MM-DD format)
            date_str = request.form["date"]
            from datetime import datetime

            date_obj = datetime.strptime(date_str, "%Y-%m-%d")
            year = date_obj.year
            month = date_obj.month
            day = date_obj.day
        except ValueError:
            return jsonify({"error": "Invalid date format. Use YYYY-MM-DD"}), 400

        # Check for trimming parameters
        trim_start = request.form.get("trimStart")
        trim_end = request.form.get("trimEnd")

        audio_service = AudioService()

        # If trimming parameters are provided, handle audio trimming
        if trim_start is not None and trim_end is not None:
            try:
                start_time = float(trim_start)
                end_time = float(trim_end)

                if start_time < 0 or end_time <= start_time:
                    return jsonify({"error": "Invalid trim times"}), 400

                filename = audio_service.save_audio_file_with_trim(
                    file, child_name, word_text, year, month, day, start_time, end_time
                )
            except ValueError:
                return jsonify({"error": "Invalid trim time format"}), 400
        else:
            # Save without trimming
            filename = audio_service.save_audio_file(file, child_name, word_text, year, month, day)

        if filename:
            word.add_recording(year, month, day, filename)
            data_service.save_child(child)
            return jsonify({"year": year, "month": month, "day": day, "filename": filename})
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
        file_path = audio_service.get_audio_file_path(child_name, word_text, filename)
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
    "/children/<child_name>/words/<word_text>/recordings/<int:year>/<int:month>/<int:day>",
    methods=["DELETE"],
)
def delete_recording(child_name, word_text, year, month, day):
    """Delete a recording for a specific date"""
    try:
        # Validate date by trying to create a date object
        from datetime import date

        try:
            date(year, month, day)
        except ValueError:
            return jsonify({"error": "Invalid date"}), 400

        data_service = DataService()
        child = data_service.get_child(child_name)
        if not child:
            return jsonify({"error": "Child not found"}), 404

        word = child.get_word(word_text)
        if not word:
            return jsonify({"error": "Word not found"}), 404

        recording = word.get_recording(year, month, day)
        if not recording:
            return jsonify({"error": "Recording not found"}), 404

        # Delete the audio file
        audio_service = AudioService()
        audio_service.delete_audio_file(child_name, word_text, recording.filename)

        # Remove from word
        word.remove_recording(year, month, day)
        data_service.save_child(child)

        return jsonify({"message": "Recording deleted successfully"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@api.route("/children/<child_name>/words/<word_text>", methods=["DELETE"])
def delete_word(child_name, word_text):
    """Delete a word and all its recordings and images"""
    try:
        data_service = DataService()
        child = data_service.get_child(child_name)
        if not child:
            return jsonify({"error": "Child not found"}), 404

        word = child.get_word(word_text)
        if not word:
            return jsonify({"error": "Word not found"}), 404

        # Delete all audio files for this word
        audio_service = AudioService()
        for recording in word.recordings:
            audio_service.delete_audio_file(child_name, word_text, recording.filename)

        # Delete the word image if it exists
        image_service = ImageService()
        image_service.delete_image_file(word_text)

        # Remove the word from the child
        child.remove_word(word_text)
        data_service.save_child(child)

        return jsonify({"message": "Word deleted successfully"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@api.route("/search/images", methods=["GET"])
def search_images():
    """Search for images using external API"""
    try:
        query = request.args.get("q", "").strip()
        if not query:
            return jsonify({"error": "Search query is required"}), 400

        page = int(request.args.get("page", 1))
        if page < 1:
            page = 1

        image_search_service = ImageSearchService()
        results = image_search_service.search_images(query, page)

        # Check if there's an error in the results
        if "error" in results:
            return jsonify(results), 200  # Return 200 but with error message in body

        return jsonify(results)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@api.route("/children/<child_name>/words/<word_text>/image/download", methods=["POST"])
def download_word_image(child_name, word_text):
    """Download an image from URL for a word"""
    try:
        data_service = DataService()
        child = data_service.get_child(child_name)
        if not child:
            return jsonify({"error": "Child not found"}), 404

        word = child.get_word(word_text)
        if not word:
            return jsonify({"error": "Word not found"}), 404

        data = request.get_json()
        if not data or "imageUrl" not in data:
            return jsonify({"error": "Image URL is required"}), 400

        image_url = data["imageUrl"]
        if not image_url:
            return jsonify({"error": "Image URL cannot be empty"}), 400

        # Download and save the image
        image_search_service = ImageSearchService()
        filename = image_search_service.download_image(image_url, word_text)

        if not filename:
            return jsonify({"error": "Failed to download image"}), 500

        # Update the word with the new image
        word.image_filename = filename
        data_service.save_child(child)

        return jsonify({"message": "Image downloaded and saved successfully", "filename": filename})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
