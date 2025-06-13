from dataclasses import dataclass


@dataclass
class Recording:
    """Represents an audio recording for a specific year"""

    year: int
    filename: str

    def __init__(self, year: int, filename: str):
        self.year = year
        self.filename = filename

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization"""
        return {"year": self.year, "filename": self.filename}

    @classmethod
    def from_dict(cls, data: dict) -> "Recording":
        """Create Recording instance from dictionary"""
        return cls(year=data["year"], filename=data["filename"])
