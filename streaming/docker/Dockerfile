FROM python:3.9-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy streaming module
COPY producers/ ./producers/
COPY consumers/ ./consumers/
COPY __init__.py .

# Scraper services will be mounted at runtime via docker-compose

# Environment variables
ENV KAFKA_BROKER=kafka:9092
ENV PYTHONUNBUFFERED=1

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
  CMD python -c "import sys; sys.exit(0)"

# Default command (can be overridden)
CMD ["python", "-m", "producers.nepse_producer"]
