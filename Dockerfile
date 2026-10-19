# HomzDoctor API image for Google Cloud Run. Build with repository root as context.
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    ENVIRONMENT=production \
    DEBUG=false \
    HOST=0.0.0.0 \
    PORT=8080 \
    SEED_DEMO_DATA=false

WORKDIR /app

# asyncpg and other optional production adapters were previously omitted from the API image.
COPY backend/requirements.txt backend/requirements-production.txt ./
RUN python -m pip install --no-cache-dir --upgrade pip \
    && python -m pip install --no-cache-dir -r requirements.txt -r requirements-production.txt

# .dockerignore excludes test fixtures, local credentials, uploaded medical files and seed data.
COPY backend/ ./

RUN addgroup --system homzdoctor \
    && adduser --system --ingroup homzdoctor --home /app homzdoctor \
    && mkdir -p /app/uploads \
    && chown -R homzdoctor:homzdoctor /app

USER homzdoctor

EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=5s --start-period=45s --retries=3 \
  CMD ["python", "-c", "import os, urllib.request; urllib.request.urlopen('http://127.0.0.1:' + os.getenv('PORT', '8080') + '/health', timeout=4)"]

CMD ["sh", "-c", "exec uvicorn main:app --host 0.0.0.0 --port ${PORT:-8080}"]
