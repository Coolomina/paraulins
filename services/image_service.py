import os
from typing import Optional
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename
from PIL import Image
from config import Config


class ImageService:
    """Service for managing image files"""

    def __init__(self):
        self.images_dir = Config.IMAGES_DIR
        self.allowed_extensions = Config.ALLOWED_IMAGE_EXTENSIONS
        self.max_file_size = Config.MAX_IMAGE_SIZE

    def _allowed_file(self, filename: str) -> bool:
        """Check if file extension is allowed"""
        return (
            "." in filename and
            filename.rsplit(".", 1)[1].lower() in self.allowed_extensions
        )

    def _get_image_path(self, word: str, extension: str) -> str:
        """Get the full path for an image file"""
        filename = f"{secure_filename(word)}.{extension}"
        return os.path.join(self.images_dir, filename)

    def save_image_file(self, file: FileStorage, word: str) -> Optional[str]:
        """Save an image file and return the filename"""
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
        file_path = self._get_image_path(word, extension)

        # Remove existing image for this word
        self.delete_image_file(word)

        # Save and optimize the image
        try:
            with Image.open(file) as img:
                # Convert to RGB if necessary
                if img.mode in ("RGBA", "LA", "P"):
                    img = img.convert("RGB")

                # Resize if too large (max 800px on longest side)
                max_size = 800
                if max(img.size) > max_size:
                    img.thumbnail(
                        (max_size, max_size), Image.Resampling.LANCZOS
                    )

                # Save with optimization
                if extension.lower() in ("jpg", "jpeg"):
                    img.save(file_path, "JPEG", quality=85, optimize=True)
                else:
                    img.save(file_path, optimize=True)
        except Exception as e:
            raise ValueError(f"Error processing image: {str(e)}")

        # Return just the filename for storage in data
        return f"{secure_filename(word)}.{extension}"

    def get_image_file_path(self, filename: str) -> Optional[str]:
        """Get the full path to an image file"""
        file_path = os.path.join(self.images_dir, filename)
        if os.path.exists(file_path):
            return file_path
        return None

    def delete_image_file(self, word: str) -> bool:
        """Delete image file(s) for a word"""
        deleted = False
        word_safe = secure_filename(word)

        # Check for any existing images with this word name
        for ext in self.allowed_extensions:
            filename = f"{word_safe}.{ext}"
            file_path = os.path.join(self.images_dir, filename)
            if os.path.exists(file_path):
                os.remove(file_path)
                deleted = True

        return deleted

    def get_image_filename(self, word: str) -> Optional[str]:
        """Get the image filename for a word if it exists"""
        word_safe = secure_filename(word)

        for ext in self.allowed_extensions:
            filename = f"{word_safe}.{ext}"
            file_path = os.path.join(self.images_dir, filename)
            if os.path.exists(file_path):
                return filename

        return None
