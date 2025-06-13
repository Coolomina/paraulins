# 🎙️ Family Voices - Pronunciation Evolution Tracker

Track your children's pronunciation evolution over time with this modern web application. Record, upload, and organize audio recordings with visual waveform editing.

[![Python](https://img.shields.io/badge/python-3.12-blue.svg)](https://python.org)
[![Flask](https://img.shields.io/badge/flask-2.3+-green.svg)](https://flask.palletsprojects.com/)
[![Docker](https://img.shields.io/badge/docker-supported-blue.svg)](https://docker.com)

## ✨ Key Features

- **Multi-child management** with individual vocabularies
- **Browser recording** or **file upload** (MP3, WAV, OGG, M4A, WebM)
- **Visual waveform trimming** with click-and-drag selection
- **Date-precise tracking** (daily, monthly, yearly organization)
- **Image associations** for words
- **Mobile-responsive** Bootstrap 5 interface
- **Local file storage** (no cloud uploads)

## 🚀 Quick Start

### Docker (Recommended)
```bash
git clone <repository-url> && cd voices
docker build -t family-voices .
docker run -p 5001:5001 -v $(pwd)/data:/app/data family-voices
```

### Local Development
```bash
git clone <repository-url> && cd voices
pdm install
pdm run start
```

Open `http://localhost:5001`

## 🛠️ Development

### Setup
```bash
pdm install                # Install dependencies
pdm run pre-commit-install # Install pre-commit hooks
pdm run start              # Start development server
```

### Scripts
```bash
pdm run test          # Run tests with coverage
pdm run lint          # Run flake8 linting  
pdm run format        # Format with black
pdm run type-check    # Run mypy
```

## 📁 Project Structure

```
voices/
├── app.py                 # Flask application
├── models/               # Data models (Child, Word, Recording)
├── routes/               # API & web routes  
├── services/             # Business logic (Audio, Data, Image)
├── static/               # CSS & JavaScript
├── templates/            # HTML templates
├── tests/                # Test suite
└── data/                 # Storage (JSON + audio/image files)
```

## 🎯 Usage

1. **Add children** on the home page
2. **Add words** for each child
3. **Record audio** (browser recording or file upload)
4. **Trim audio** using the visual waveform (optional)
5. **Add images** to words for visual recognition

## 🚢 Deployment

### Docker Compose
```yaml
version: '3.8'
services:
  family-voices:
    build: .
    ports:
      - "5001:5001"
    volumes:
      - ./data:/app/data
```

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines on:

- Development setup and workflow
- Code standards and testing
- Architecture guidelines
- How to submit pull requests

**Quick start**: Fork → Clone → `pdm install` → Make changes → `pdm run test && pdm run lint` → Submit PR

## License

MIT License - see [LICENSE](LICENSE) file.
