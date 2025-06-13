import json
import os
from typing import List, Optional

from flask import current_app

from config import Config
from models.child import Child
from models.word import Word


class DataService:
    """Service for managing application data persistence"""

    def __init__(self):
        # Use Flask app config if available, otherwise fallback to Config class
        try:
            self.data_file = current_app.config["DATA_FILE"]
        except RuntimeError:
            # No app context, use default config
            self.data_file = Config.DATA_FILE
        self._ensure_data_file_exists()

    def _ensure_data_file_exists(self) -> None:
        """Create data file if it doesn't exist"""
        if not os.path.exists(self.data_file):
            initial_data = {"children": []}
            self.save_data(initial_data)

    def load_data(self) -> dict:
        """Load data from JSON file"""
        try:
            with open(self.data_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {"children": []}

    def save_data(self, data: dict) -> None:
        """Save data to JSON file"""
        with open(self.data_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def get_children(self) -> List[Child]:
        """Get all children"""
        data = self.load_data()
        return [Child.from_dict(child_data) for child_data in data.get("children", [])]

    def get_child(self, name: str) -> Optional[Child]:
        """Get a specific child by name"""
        children = self.get_children()
        return next((child for child in children if child.name == name), None)

    def save_child(self, child: Child) -> None:
        """Save or update a child"""
        data = self.load_data()
        children = data.get("children", [])

        # Remove existing child with same name
        children = [c for c in children if c["name"] != child.name]

        # Add updated child
        children.append(child.to_dict())

        data["children"] = children
        self.save_data(data)

    def delete_child(self, name: str) -> bool:
        """Delete a child"""
        data = self.load_data()
        children = data.get("children", [])

        original_length = len(children)
        children = [c for c in children if c["name"] != name]

        if len(children) < original_length:
            data["children"] = children
            self.save_data(data)
            return True
        return False

    def add_word_to_child(self, child_name: str, word: Word) -> bool:
        """Add a word to a child's vocabulary"""
        child = self.get_child(child_name)
        if child:
            child.add_word(word)
            self.save_child(child)
            return True
        return False

    def add_recording_to_word(
        self, child_name: str, word_text: str, year: int, month: int, day: int, filename: str
    ) -> bool:
        """Add a recording to a word"""
        child = self.get_child(child_name)
        if child:
            word = child.get_word(word_text)
            if word:
                word.add_recording(year, month, day, filename)
                self.save_child(child)
                return True
        return False
