# Backend-only image. For Google Cloud Run from the repository root, use ../Dockerfile.
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    HOST=0.0.0.0 \
    PORT=8000

WORKDIR /app

# Install runtime dependencies for both SQLite development and production PostgreSQL.
# requirements-production.txt supplies asyncpg, Redis, Qdrant and hosted model clients.
COPY requirements.txt requirements-production.txt ./
RUN python -m pip install --no-cache-dir --upgrade pip \
    && python -m pip install --no-cache-dir -r requirements.txt -r requirements-production.txt

COPY . .

RUN mkdir -p /app/uploads
EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=40s --retries=3 \
  CMD python -c "import os, urllib.request; urllib.request.urlopen('http://127.0.0.1:' + os.getenv('PORT', '8000') + '/health', timeout=4)"

CMD ["sh", "-c", "exec uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}"]
