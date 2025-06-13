from dataclasses import dataclass
from datetime import datetime


@dataclass
class Recording:
    """Represents an audio recording for a specific month and year"""

    year: int
    month: int
    filename: str

    def __init__(self, year: int, month: int, filename: str):
        if not (1 <= month <= 12):
            raise ValueError("Month must be between 1 and 12")
        if year < 2000 or year > 2050:
            raise ValueError("Year must be between 2000 and 2050")
            
        self.year = year
        self.month = month
        self.filename = filename

    @property
    def date_string(self) -> str:
        """Get a formatted date string (YYYY-MM)"""
        return f"{self.year}-{self.month:02d}"
    
    @property
    def display_date(self) -> str:
        """Get a human-readable date string"""
        month_names = [
            "Jan", "Feb", "Mar", "Apr", "May", "Jun",
            "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"
        ]
        return f"{month_names[self.month - 1]} {self.year}"

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization"""
        return {
            "year": self.year,
            "month": self.month,
            "filename": self.filename
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Recording":
        """Create Recording instance from dictionary"""
        # Handle legacy data that only has year
        if "month" not in data:
            # Default to January for legacy recordings
            month = 1
        else:
            month = data["month"]
            
        return cls(
            year=data["year"],
            month=month,
            filename=data["filename"]
        )
