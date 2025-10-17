# syntax=docker/dockerfile:1.6
#
# Optimized, cache-friendly Dockerfile for Django backend (Python 3.12 slim)
# - Separates dependency installation from app source to maximize layer caching
# - Uses pip cache mount to speed repeated builds
# - Minimizes apt packages and cleans up caches
# - Avoids running tests/migrations/collectstatic at build time
# - Provides a lightweight runtime image
#
# Usage:
#   docker build -t voice-chatbot-backend:latest .
#   docker run --env-file .env -p 3001:3001 voice-chatbot-backend:latest
#
# Notes:
# - This image uses gunicorn for production-like serving; adjust CMD if needed.
# - No heavy audio libs are installed by default to keep image slim. The app
#   gracefully falls back if pyttsx3/system audio isn't available.

ARG PYTHON_VERSION=3.12-slim
FROM python:${PYTHON_VERSION} AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=0 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_DEFAULT_TIMEOUT=100

WORKDIR /app

# System dependencies (minimal). Avoid heavy audio libs by default.
# Add only what is necessary for building wheels for common Python libs.
# We install build-essential and libffi-dev for potential wheels; remove them in final image.
RUN --mount=type=cache,target=/var/cache/apt \
    apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
      build-essential \
      libffi-dev \
      curl \
      ca-certificates && \
    rm -rf /var/lib/apt/lists/*

# Upgrade pip and install wheel to speed up installs
RUN python -m pip install --upgrade pip setuptools wheel

# Stage dedicated to dependencies using requirements.txt with caching.
FROM base AS deps
# Copy only requirements first to enable Docker layer caching
COPY requirements.txt /app/requirements.txt

# Install Python deps with pip cache mounted to speed up repeated builds
# We also generate a frozen requirements file for deterministic installs at build time.
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --no-compile -r /app/requirements.txt && \
    pip freeze --all | sed '/^pkg-resources==/d' > /app/requirements.lock

# Final runtime image (lighter)
FROM python:${PYTHON_VERSION} AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DJANGO_SETTINGS_MODULE=config.settings \
    PORT=3001 \
    GUNICORN_CMD_ARGS="--bind 0.0.0.0:3001 --workers 3 --threads 2 --timeout 60"

WORKDIR /app

# Install minimal runtime system deps (no build-essential kept)
RUN --mount=type=cache,target=/var/cache/apt \
    apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
      ca-certificates \
      curl && \
    rm -rf /var/lib/apt/lists/*

# Copy site-packages from deps stage
COPY --from=deps /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=deps /usr/local/bin /usr/local/bin

# Copy application source last to maximize caching
COPY . /app

# Expose app port
EXPOSE 3001

# Healthcheck (simple HTTP probe to /api/health)
HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
  CMD curl -fsS http://localhost:${PORT}/api/health/ || exit 1

# Do not run migrations/collectstatic at build-time; keep runtime startup fast and predictable.
# Use gunicorn for serving; for development you can override the CMD to run the Django dev server.
CMD ["gunicorn", "config.wsgi:application"]
