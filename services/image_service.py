import os
from typing import Optional

from PIL import Image
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename

from config import Config


class ImageService:
    """Service for managing image files"""

    def __init__(self):
        self.images_dir = Config.IMAGES_DIR
        self.allowed_extensions = Config.ALLOWED_IMAGE_EXTENSIONS
        self.max_file_size = Config.MAX_IMAGE_SIZE

    def _allowed_file(self, filename: str) -> bool:
        """Check if file extension is allowed"""
        return "." in filename and filename.rsplit(".", 1)[1].lower() in self.allowed_extensions

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
        file_path = self._get_image_path(word, extension)

        # Remove existing image for this word
        self.delete_image_file(word)

        # Save and optimize the image
        try:
            with Image.open(file) as img:
                # Convert to RGB if necessary
                if img.mode in ("RGBA", "LA", "P"):
                    img = img.convert("RGB")

                # Resize to a reasonable size for word cards
                # Target size: 240px (3x the display size for crisp quality on high-DPI screens)
                target_size = 240

                # Only resize if image is larger than target
                if max(img.size) > target_size:
                    # Calculate new dimensions maintaining aspect ratio
                    ratio = min(target_size / img.width, target_size / img.height)
                    new_width = int(img.width * ratio)
                    new_height = int(img.height * ratio)

                    # Use high-quality resampling
                    img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)

                # Apply slight sharpening for better appearance at small sizes
                from PIL import ImageFilter

                img = img.filter(ImageFilter.UnsharpMask(radius=0.5, percent=50, threshold=2))

                # Save with optimization
                if extension.lower() in ("jpg", "jpeg"):
                    img.save(file_path, "JPEG", quality=90, optimize=True)
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
