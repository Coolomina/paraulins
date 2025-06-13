import os
import tempfile
from typing import List, Optional

from pydub import AudioSegment
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
        return "." in filename and filename.rsplit(".", 1)[1].lower() in self.allowed_extensions

    def _get_audio_path(
        self, child_name: str, word: str, year: int, month: int, day: int, extension: str
    ) -> str:
        """Get the full path for an audio file"""
        child_dir = os.path.join(self.audio_dir, secure_filename(child_name))
        word_dir = os.path.join(child_dir, secure_filename(word))
        os.makedirs(word_dir, exist_ok=True)
        return os.path.join(word_dir, f"{year}-{month:02d}-{day:02d}.{extension}")

    def _get_audio_path_legacy_month(
        self, child_name: str, word: str, year: int, month: int, extension: str
    ) -> str:
        """Get the full path for an audio file (legacy month format)"""
        child_dir = os.path.join(self.audio_dir, secure_filename(child_name))
        word_dir = os.path.join(child_dir, secure_filename(word))
        os.makedirs(word_dir, exist_ok=True)
        return os.path.join(word_dir, f"{year}-{month:02d}.{extension}")

    def _get_audio_path_legacy(self, child_name: str, word: str, year: int, extension: str) -> str:
        """Get the full path for an audio file (legacy format)"""
        child_dir = os.path.join(self.audio_dir, secure_filename(child_name))
        word_dir = os.path.join(child_dir, secure_filename(word))
        os.makedirs(word_dir, exist_ok=True)
        return os.path.join(word_dir, f"{year}.{extension}")

    def save_audio_file(
        self, file: FileStorage, child_name: str, word: str, year: int, month: int, day: int
    ) -> Optional[str]:
        """Save an audio file and return the filename"""
        if not file or not file.filename:
            return None

        if not self._allowed_file(file.filename):
            raise ValueError(
                f"File type not allowed. Allowed types: " f"{', '.join(self.allowed_extensions)}"
            )

        # Check file size
        file.seek(0, 2)  # Seek to end
        file_size = file.tell()
        file.seek(0)  # Reset to beginning

        if file_size > self.max_file_size:
            max_size_mb = self.max_file_size / 1024 / 1024
            raise ValueError(f"File too large. Maximum size: {max_size_mb:.1f}MB")

        # Get file extension
        extension = file.filename.rsplit(".", 1)[1].lower()

        # Create the file path
        file_path = self._get_audio_path(child_name, word, year, month, day, extension)

        # Save the file
        file.save(file_path)

        # Return just the filename for storage in data
        return f"{year}-{month:02d}-{day:02d}.{extension}"

    def save_audio_file_with_trim(
        self,
        file: FileStorage,
        child_name: str,
        word: str,
        year: int,
        month: int,
        day: int,
        start_time: float,
        end_time: float,
    ) -> Optional[str]:
        """Save an audio file with trimming and return the filename"""
        if not file or not file.filename:
            return None

        if not self._allowed_file(file.filename):
            raise ValueError(
                f"File type not allowed. Allowed types: " f"{', '.join(self.allowed_extensions)}"
            )

        # Check file size
        file.seek(0, 2)  # Seek to end
        file_size = file.tell()
        file.seek(0)  # Reset to beginning

        if file_size > self.max_file_size:
            max_size_mb = self.max_file_size / 1024 / 1024
            raise ValueError(f"File too large. Maximum size: {max_size_mb:.1f}MB")

        # Get file extension
        extension = file.filename.rsplit(".", 1)[1].lower()

        # Create temporary file to save the original
        with tempfile.NamedTemporaryFile(suffix=f".{extension}", delete=False) as temp_file:
            file.save(temp_file.name)
            temp_path = temp_file.name

        try:
            # Load audio with pydub
            audio = AudioSegment.from_file(temp_path)

            # Convert times to milliseconds
            start_ms = int(start_time * 1000)
            end_ms = int(end_time * 1000)

            # Validate trim times
            if start_ms < 0:
                start_ms = 0
            if end_ms > len(audio):
                end_ms = len(audio)
            if start_ms >= end_ms:
                raise ValueError("Invalid trim times: start must be before end")

            # Trim the audio
            trimmed_audio = audio[start_ms:end_ms]

            # Create the file path
            file_path = self._get_audio_path(child_name, word, year, month, day, extension)

            # Export the trimmed audio
            # Use the original format for export
            if extension in ["mp3"]:
                trimmed_audio.export(file_path, format="mp3")
            elif extension in ["wav"]:
                trimmed_audio.export(file_path, format="wav")
            elif extension in ["ogg"]:
                trimmed_audio.export(file_path, format="ogg")
            elif extension in ["m4a"]:
                trimmed_audio.export(file_path, format="mp4")
            elif extension in ["webm"]:
                # WebM is not directly supported by pydub, convert to ogg
                ogg_path = file_path.replace(".webm", ".ogg")
                trimmed_audio.export(ogg_path, format="ogg")
                # Update the extension and filename
                extension = "ogg"
                file_path = ogg_path
            else:
                # Default to wav for unsupported formats
                wav_path = file_path.replace(f".{extension}", ".wav")
                trimmed_audio.export(wav_path, format="wav")
                extension = "wav"
                file_path = wav_path

            # Return just the filename for storage in data
            return f"{year}-{month:02d}-{day:02d}.{extension}"

        except Exception as e:
            raise ValueError(f"Error processing audio: {str(e)}")
        finally:
            # Clean up temporary file
            if os.path.exists(temp_path):
                os.unlink(temp_path)

    def get_audio_file_path(self, child_name: str, word: str, filename: str) -> Optional[str]:
        """Get the full path to an audio file"""
        child_dir = os.path.join(self.audio_dir, secure_filename(child_name))
        word_dir = os.path.join(child_dir, secure_filename(word))
        file_path = os.path.join(word_dir, filename)

        if os.path.exists(file_path):
            return file_path
        return None

    def delete_audio_file(self, child_name: str, word: str, filename: str) -> bool:
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
