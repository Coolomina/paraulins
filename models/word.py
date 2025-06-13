from dataclasses import dataclass, field
from typing import List, Optional

from .recording import Recording


@dataclass
class Word:
    """Represents a word with its recordings and optional image"""

    text: str
    image_filename: Optional[str] = None
    recordings: List[Recording] = field(default_factory=list)

    def __init__(
        self,
        text: str,
        image_filename: Optional[str] = None,
        recordings: Optional[List[Recording]] = None,
    ):
        self.text = text
        self.image_filename = image_filename
        self.recordings = recordings or []

    def add_recording(self, year: int, month: int, day: int, filename: str) -> None:
        """Add a recording for a specific date"""
        # Remove existing recording for this date if it exists
        self.recordings = [
            r for r in self.recordings if not (r.year == year and r.month == month and r.day == day)
        ]
        self.recordings.append(Recording(year, month, day, filename))
        # Sort by date (year, month, day)
        self.recordings.sort(key=lambda r: (r.year, r.month, r.day))

    def get_recording(self, year: int, month: int, day: int) -> Optional[Recording]:
        """Get recording for a specific date"""
        return next(
            (r for r in self.recordings if r.year == year and r.month == month and r.day == day),
            None,
        )

    def remove_recording(self, year: int, month: int, day: int) -> bool:
        """Remove recording for a specific date"""
        recording = self.get_recording(year, month, day)
        if recording:
            self.recordings.remove(recording)
            return True
        return False

    # Legacy methods for backward compatibility
    def add_recording_legacy(self, year: int, month: int, filename: str) -> None:
        """Add a recording for a specific month and year (legacy - defaults to 1st day)"""
        self.add_recording(year, month, 1, filename)

    def get_recording_legacy(self, year: int, month: int) -> Optional[Recording]:
        """Get recording for a specific month and year (legacy - gets first recording of that month)"""
        month_recordings = [r for r in self.recordings if r.year == year and r.month == month]
        return month_recordings[0] if month_recordings else None

    def get_dates(self) -> List[tuple]:
        """Get all (year, month) tuples that have recordings"""
        return sorted([(r.year, r.month) for r in self.recordings])

    def get_years(self) -> List[int]:
        """Get all years that have recordings (for backward compatibility)"""
        return sorted(list(set([r.year for r in self.recordings])))

    def set_image(self, filename: str) -> None:
        """Set the image filename for this word"""
        self.image_filename = filename

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization"""
        return {
            "text": self.text,
            "image_filename": self.image_filename,
            "recordings": [recording.to_dict() for recording in self.recordings],
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Word":
        """Create Word instance from dictionary"""
        recordings = [Recording.from_dict(rec_data) for rec_data in data.get("recordings", [])]
        return cls(
            text=data["text"], image_filename=data.get("image_filename"), recordings=recordings
        )
