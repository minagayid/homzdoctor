# Standalone backend image for Docker hosts and container platforms.
# For Google Cloud Run from repository root, use the root ../Dockerfile.
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    ENVIRONMENT=production \
    DEBUG=false \
    SEED_DEMO_DATA=false \
    HOST=0.0.0.0 \
    PORT=8000

WORKDIR /app

# Install both base and production adapters (including asyncpg for PostgreSQL).
COPY requirements.txt requirements-production.txt ./
RUN python -m pip install --no-cache-dir --upgrade pip \
    && python -m pip install --no-cache-dir -r requirements.txt -r requirements-production.txt

COPY . .

RUN addgroup --system homzdoctor \
    && adduser --system --ingroup homzdoctor --home /app homzdoctor \
    && mkdir -p /app/uploads \
    && chown -R homzdoctor:homzdoctor /app

USER homzdoctor
EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=40s --retries=3 \
  CMD ["python", "-c", "import os, urllib.request; urllib.request.urlopen('http://127.0.0.1:' + os.getenv('PORT', '8000') + '/health', timeout=4)"]

CMD ["sh", "-c", "exec uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}"]
