import os
from typing import Optional, List
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename
from config import Config


class AudioService:
    """Service for managing audio files"""

    def __init__(self):
        self.audio_dir = Config.AUDIO_DIR
        self.allowed_extensions = Config.ALLOWED_AUDIO_EXTENSIONS
        self.max_file_size = Config.MAX_AUDIO_SIZE

    def _allowed_file(self, filename: str) -> bool:
        """Check if file extension is allowed"""
        return (
            "." in filename and
            filename.rsplit(".", 1)[1].lower() in self.allowed_extensions
        )

    def _get_audio_path(
        self, child_name: str, word: str, year: int, extension: str
    ) -> str:
        """Get the full path for an audio file"""
        child_dir = os.path.join(self.audio_dir, secure_filename(child_name))
        word_dir = os.path.join(child_dir, secure_filename(word))
        os.makedirs(word_dir, exist_ok=True)
        return os.path.join(word_dir, f"{year}.{extension}")

    def save_audio_file(
        self, file: FileStorage, child_name: str, word: str, year: int
    ) -> Optional[str]:
        """Save an audio file and return the filename"""
        if not file or not file.filename:
            return None

        if not self._allowed_file(file.filename):
            raise ValueError(
                f"File type not allowed. Allowed types: "
                f"{', '.join(self.allowed_extensions)}"
            )

        # Check file size
        file.seek(0, 2)  # Seek to end
        file_size = file.tell()
        file.seek(0)  # Reset to beginning

        if file_size > self.max_file_size:
            max_size_mb = self.max_file_size / 1024 / 1024
            raise ValueError(
                f"File too large. Maximum size: {max_size_mb:.1f}MB"
            )

        # Get file extension
        extension = file.filename.rsplit(".", 1)[1].lower()

        # Create the file path
        file_path = self._get_audio_path(child_name, word, year, extension)

        # Save the file
        file.save(file_path)

        # Return just the filename for storage in data
        return f"{year}.{extension}"

    def get_audio_file_path(
        self, child_name: str, word: str, filename: str
    ) -> Optional[str]:
        """Get the full path to an audio file"""
        child_dir = os.path.join(self.audio_dir, secure_filename(child_name))
        word_dir = os.path.join(child_dir, secure_filename(word))
        file_path = os.path.join(word_dir, filename)

        if os.path.exists(file_path):
            return file_path
        return None

    def delete_audio_file(
        self, child_name: str, word: str, filename: str
    ) -> bool:
        """Delete an audio file"""
        file_path = self.get_audio_file_path(child_name, word, filename)
        if file_path and os.path.exists(file_path):
            os.remove(file_path)

            # Clean up empty directories
            word_dir = os.path.dirname(file_path)
            if not os.listdir(word_dir):
                os.rmdir(word_dir)

                child_dir = os.path.dirname(word_dir)
                if not os.listdir(child_dir):
                    os.rmdir(child_dir)

            return True
        return False

    def get_all_audio_files(self, child_name: str, word: str) -> List[str]:
        """Get all audio files for a word"""
        child_dir = os.path.join(self.audio_dir, secure_filename(child_name))
        word_dir = os.path.join(child_dir, secure_filename(word))

        if not os.path.exists(word_dir):
            return []

        files = []
        for filename in os.listdir(word_dir):
            if self._allowed_file(filename):
                files.append(filename)

        return sorted(files)
