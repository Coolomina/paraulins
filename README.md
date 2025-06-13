# Family Voices - Pronunciation Evolution Tracker

A webapp to track and listen to the evolution of your children's pronunciation of words over the years.

## Features

- Select between your two daughters
- Manage words for each child with audio recordings by **month and year**
- **Browser-based recording**: Record directly in your browser with microphone access
- **File upload option**: Upload pre-recorded audio files
- Attach images to words for easy recognition
- Play audio recordings organized chronologically
- File-based storage (no database required)

### Recording Options

The app provides two convenient ways to add audio recordings:

1. **Record Now**: Click the microphone button to record directly in your browser
   - Automatically requests microphone permission
   - Visual recording timer with progress bar
   - 60-second maximum recording time
   - Preview and re-record functionality
   - Supports multiple audio formats (WebM, OGG, MP4)

2. **Upload File**: Upload pre-recorded audio files
   - Supports MP3, WAV, OGG, M4A, and WebM formats
   - Maximum file size: 10MB

### Monthly Tracking

Recordings are now organized by **month and year** instead of just year, giving you much better granularity to track pronunciation evolution. You can:

- Record multiple times per year
- See progression month by month
- Compare recordings from the same month across different years
- Default to current month when adding new recordings

## Quick Start

Using PDM and Make:
```bash
# Setup development environment (one-time)
make setup-dev

# Run the application
make run

# Run tests
make test

# Run all quality checks
make check
```

Manual setup:

1. Install PDM (if not already installed):
```bash
pip install pdm
```

2. Install dependencies and create virtual environment:
```bash
pdm install
```

3. Create the data directories:
```bash
mkdir -p data/audio data/images
```

4. Run the application:
```bash
pdm run start
```

5. Open your browser to `http://localhost:5000`

## Development

### Running Tests
```bash
# Run all tests
pdm run test

# Run tests with coverage
pdm run test-cov
```

### Code Quality
```bash
# Format code
pdm run format

# Lint code
pdm run lint

# Type checking
pdm run type-check
```

### Installing Additional Dependencies
```bash
# Add a runtime dependency
pdm add package_name

# Add a development dependency
pdm add -dG dev package_name

# Add a test dependency
pdm add -dG test package_name
```

## Project Structure

```
voices/
├── app.py                 # Flask application entry point
├── models/
│   ├── __init__.py
│   ├── child.py          # Child model
│   ├── word.py           # Word model
│   └── recording.py      # Recording model
├── services/
│   ├── __init__.py
│   ├── audio_service.py  # Audio file management
│   ├── image_service.py  # Image file management
│   └── data_service.py   # Data persistence
├── routes/
│   ├── __init__.py
│   ├── api.py            # REST API routes
│   └── web.py            # Web interface routes
├── static/               # CSS, JS, images
├── templates/            # HTML templates
├── data/                 # Data storage
│   ├── audio/           # Audio files
│   ├── images/          # Word images
│   └── data.json        # Application data
├── tests/               # Unit tests
└── config.py            # Configuration
```

## Data Structure

Audio files are stored as: `data/audio/{child_name}/{word}/{year}.mp3`
Images are stored as: `data/images/{word}.jpg`
Metadata is stored in: `data/data.json`
