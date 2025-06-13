from dataclasses import dataclass
from typing import List, Optional
from .word import Word


@dataclass
class Child:
    """Represents a child in the system"""

    name: str
    words: List[Word]

    def __init__(self, name: str, words: Optional[List[Word]] = None):
        self.name = name
        self.words = words or []

    def add_word(self, word: Word) -> None:
        """Add a word to this child's vocabulary"""
        if not any(w.text == word.text for w in self.words):
            self.words.append(word)

    def get_word(self, word_text: str) -> Optional[Word]:
        """Get a specific word by text"""
        return next((w for w in self.words if w.text == word_text), None)

    def remove_word(self, word_text: str) -> bool:
        """Remove a word from this child's vocabulary"""
        word = self.get_word(word_text)
        if word:
            self.words.remove(word)
            return True
        return False

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization"""
        return {
            "name": self.name,
            "words": [word.to_dict() for word in self.words]
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Child":
        """Create Child instance from dictionary"""
        words = [
            Word.from_dict(word_data) for word_data in data.get("words", [])
        ]
        return cls(name=data["name"], words=words)
