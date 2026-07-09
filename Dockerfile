FROM python:3.10-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    TTS_ENGINE=edge_tts \
    CLOUD_MODE=1 \
    OMP_NUM_THREADS=1 \
    OPENBLAS_NUM_THREADS=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    fonts-dejavu-core \
    libglib2.0-0 \
    libgl1 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY agents ./agents
COPY backend ./backend
COPY mcp ./mcp
COPY shared ./shared
COPY state_manager ./state_manager
COPY scripts ./scripts
COPY tests ./tests
COPY data/outputs/.gitkeep ./data/outputs/.gitkeep
COPY data/state_versions/.gitkeep ./data/state_versions/.gitkeep

RUN mkdir -p data/outputs data/state_versions

EXPOSE 8001

HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD python -c "import os,urllib.request; urllib.request.urlopen(f'http://localhost:{os.getenv(\"PORT\", \"8001\")}/health')"

CMD ["sh", "-c", "uvicorn backend.app:app --host 0.0.0.0 --port ${PORT:-8001}"]
