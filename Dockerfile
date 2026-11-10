# Dawai Saathi - Voice-first Medicine Helper for Rural India
FROM python:3.10-slim

# Install system dependencies including FFmpeg for browser audio conversion
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Create persistent storage directories
RUN mkdir -p out/audio_cache out/uploads

# Expose port
EXPOSE 8000

ENV PORT=8000
ENV HOST=0.0.0.0

# Start server with dynamic Render PORT support
CMD ["sh", "-c", "uvicorn backend.main:app --host 0.0.0.0 --port ${PORT:-8000}"]

