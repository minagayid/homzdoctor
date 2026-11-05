# Optional standalone ML inference service (CPU-only portable image).
# Model weights and datasets are deliberately not copied into this image.
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    HOST=0.0.0.0 \
    PORT=8080

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        ca-certificates \
        gcc \
        g++ \
        libgl1 \
        libglib2.0-0 \
        libsm6 \
        libxext6 \
        libxrender1 \
        libgomp1 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./
# Pin CPU wheels so a CPU-only cloud container does not pull unnecessary CUDA runtimes.
RUN python -m pip install --no-cache-dir --upgrade pip \
    && python -m pip install --no-cache-dir --index-url https://download.pytorch.org/whl/cpu torch==2.2.0 torchvision==0.17.0 \
    && python -m pip install --no-cache-dir -r requirements.txt

COPY . .

RUN addgroup --system homzdoctor-ml \
    && adduser --system --ingroup homzdoctor-ml --home /app homzdoctor-ml \
    && mkdir -p /app/models \
    && chown -R homzdoctor-ml:homzdoctor-ml /app

USER homzdoctor-ml
EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=5s --start-period=60s --retries=3 \
  CMD ["python", "-c", "import os, urllib.request; urllib.request.urlopen('http://127.0.0.1:' + os.getenv('PORT', '8080') + '/health', timeout=4)"]

CMD ["python", "inference/server.py"]
