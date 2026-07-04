# Backend Dockerfile
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create upload directory
RUN mkdir -p /app/uploads

# Expose port
EXPOSE 8000

# Run application (bind to Railway-provided $PORT, fallback to 8000)
CMD uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}
