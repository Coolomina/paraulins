FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    FLASK_APP=app.py \
    FLASK_ENV=production \
    PORT=8080

RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    libmagic1 \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

RUN pip install --no-cache-dir pdm==2.25.0

WORKDIR /app

COPY pyproject.toml pdm.lock ./

RUN mkdir -p /app/data/audio /app/data/images /app/static/uploads \
    && pdm install --prod

COPY . .

RUN printf "#!/bin/bash\ncurl -f http://localhost:\$PORT/api/health || exit 1\n" > /app/healthcheck.sh && \
    chmod +x /app/healthcheck.sh

HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD /app/healthcheck.sh

EXPOSE $PORT

CMD ["pdm", "start"]
