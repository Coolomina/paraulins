from typing import Dict, Optional

import requests

from config import Config


class ImageSearchService:
    """Service for searching images from external APIs"""

    def __init__(self):
        self.api_url = Config.IMAGE_SEARCH_API_URL
        self.api_key = Config.IMAGE_SEARCH_API_KEY
        self.results_per_page = Config.IMAGE_SEARCH_RESULTS_PER_PAGE
        self.safesearch = Config.IMAGE_SEARCH_SAFESEARCH

    def search_images(self, query: str, page: int = 1) -> Dict:
        """
        Search for images using Pixabay API

        Args:
            query: Search term
            page: Page number (1-based)

        Returns:
            Dict containing search results with images list and metadata
        """
        try:
            # Check if we have an API key
            if not self.api_key:
                # Return a helpful error message if no API key is configured
                return {
                    "total": 0,
                    "totalHits": 0,
                    "currentPage": page,
                    "perPage": self.results_per_page,
                    "images": [],
                    "error": "Image search requires a Pixabay API key. Please contact the administrator to configure this feature.",
                }

            # Prepare search parameters
            params = {
                "key": self.api_key,
                "q": query,
                "image_type": "photo",
                "orientation": "all",
                "category": "all",
                "min_width": 200,
                "min_height": 200,
                "safesearch": self.safesearch,
                "per_page": self.results_per_page,
                "page": page,
                "pretty": "false",
            }

            # Make the API request
            response = requests.get(self.api_url, params=params, timeout=10)

            # Check for specific error responses
            if response.status_code == 400:
                return {
                    "total": 0,
                    "totalHits": 0,
                    "currentPage": page,
                    "perPage": self.results_per_page,
                    "images": [],
                    "error": "Invalid search parameters. Please try different search terms.",
                }
            elif response.status_code == 429:
                return {
                    "total": 0,
                    "totalHits": 0,
                    "currentPage": page,
                    "perPage": self.results_per_page,
                    "images": [],
                    "error": "Search rate limit exceeded. Please try again later.",
                }

            response.raise_for_status()

            data = response.json()

            # Process and format the results
            processed_results = {
                "total": data.get("total", 0),
                "totalHits": data.get("totalHits", 0),
                "currentPage": page,
                "perPage": self.results_per_page,
                "images": [],
            }

            for hit in data.get("hits", []):
                image_data = {
                    "id": hit.get("id"),
                    "tags": hit.get("tags", ""),
                    "previewURL": hit.get("previewURL", ""),
                    "webformatURL": hit.get("webformatURL", ""),
                    "largeImageURL": hit.get("largeImageURL", ""),
                    "views": hit.get("views", 0),
                    "downloads": hit.get("downloads", 0),
                    "user": hit.get("user", "Unknown"),
                    "pageURL": hit.get("pageURL", ""),
                    "previewWidth": hit.get("previewWidth", 150),
                    "previewHeight": hit.get("previewHeight", 150),
                }
                processed_results["images"].append(image_data)

            return processed_results

        except requests.exceptions.RequestException as e:
            return {
                "total": 0,
                "totalHits": 0,
                "currentPage": page,
                "perPage": self.results_per_page,
                "images": [],
                "error": f"Network error: {str(e)}",
            }
        except Exception as e:
            return {
                "total": 0,
                "totalHits": 0,
                "currentPage": page,
                "perPage": self.results_per_page,
                "images": [],
                "error": f"Search error: {str(e)}",
            }

    def download_image(self, image_url: str, word: str) -> Optional[str]:
        """
        Download an image from URL and save it locally

        Args:
            image_url: URL of the image to download
            word: Word associated with the image

        Returns:
            Filename of the saved image or None if failed
        """
        try:
            # Download the image
            response = requests.get(image_url, timeout=30, stream=True)
            response.raise_for_status()

            # Check content type
            content_type = response.headers.get("content-type", "").lower()
            if not content_type.startswith("image/"):
                raise ValueError("URL does not point to an image")

            # Determine file extension from content type
            extension_map = {
                "image/jpeg": "jpg",
                "image/jpg": "jpg",
                "image/png": "png",
                "image/gif": "gif",
                "image/webp": "webp",
            }

            extension = extension_map.get(content_type, "jpg")

            # Use the existing image service to save the file
            from io import BytesIO

            from werkzeug.datastructures import FileStorage

            from services.image_service import ImageService

            # Create a file-like object from the downloaded content
            image_data = BytesIO(response.content)
            file_storage = FileStorage(
                stream=image_data,
                filename=f"downloaded_image.{extension}",
                content_type=content_type,
            )

            # Save using the existing image service
            image_service = ImageService()
            filename = image_service.save_image_file(file_storage, word)

            return filename

        except Exception as e:
            raise Exception(f"Failed to download image: {str(e)}")
