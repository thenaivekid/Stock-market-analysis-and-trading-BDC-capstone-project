# NEPSE Streamer - Containerized Service
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY nepse_live_streamer.py .
COPY nepse_live_dashboard.py .

# Copy scraper service (needed for API client)
COPY --from=scraper /app/services /app/services

# Environment variables (override with docker-compose)
ENV KAFKA_BROKER=kafka:9092
ENV STREAMING_INTERVAL=1000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
  CMD python -c "import sys; sys.exit(0)"

# Run the streamer
CMD ["sh", "-c", "python3 nepse_live_streamer.py ${STREAMING_INTERVAL}"]
