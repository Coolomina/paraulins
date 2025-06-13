from dataclasses import dataclass
from datetime import date


@dataclass
class Recording:
    """Represents an audio recording for a specific date"""

    year: int
    month: int
    day: int
    filename: str

    def __init__(self, year: int, month: int, day: int, filename: str):
        # Validate date by trying to create a date object
        try:
            date(year, month, day)
        except ValueError as e:
            raise ValueError(f"Invalid date: {year}-{month:02d}-{day:02d}") from e

        if year < 2000 or year > 2050:
            raise ValueError("Year must be between 2000 and 2050")

        self.year = year
        self.month = month
        self.day = day
        self.filename = filename

    @property
    def date_string(self) -> str:
        """Get a formatted date string (YYYY-MM-DD)"""
        return f"{self.year}-{self.month:02d}-{self.day:02d}"

    @property
    def display_date(self) -> str:
        """Get a human-readable date string"""
        date_obj = date(self.year, self.month, self.day)
        return date_obj.strftime("%b %d, %Y")  # e.g., "Jun 13, 2025"

    @property
    def short_display_date(self) -> str:
        """Get a short human-readable date string for buttons"""
        date_obj = date(self.year, self.month, self.day)
        return date_obj.strftime("%m/%d/%y")  # e.g., "06/13/25"

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization"""
        return {"year": self.year, "month": self.month, "day": self.day, "filename": self.filename}

    @classmethod
    def from_dict(cls, data: dict) -> "Recording":
        """Create Recording instance from dictionary"""
        # Handle legacy data that only has year or year/month
        year = data["year"]
        month = data.get("month", 1)  # Default to January for legacy data
        day = data.get("day", 1)  # Default to 1st day for legacy data

        return cls(year=year, month=month, day=day, filename=data["filename"])
