#!/bin/bash
# Simple Dashboard Launcher - No prompts, just runs!

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
STREAMING_DIR="$PROJECT_ROOT/streaming"
SCRAPER_DIR="$PROJECT_ROOT/scraper/app"

echo "📺 Starting NEPSE Live Dashboard..."
echo "===================================="
echo ""

# Copy files silently
echo "📦 Preparing files..."
docker exec airflow-airflow-standalone-1 mkdir -p /tmp/streaming/producers /tmp/streaming/consumers /tmp/services 2>/dev/null || true
docker cp "$STREAMING_DIR/producers/nepse_producer.py" airflow-airflow-standalone-1:/tmp/streaming/producers/ 2>/dev/null
docker cp "$STREAMING_DIR/consumers/nepse_dashboard.py" airflow-airflow-standalone-1:/tmp/streaming/consumers/ 2>/dev/null
docker cp "$SCRAPER_DIR/services/." airflow-airflow-standalone-1:/tmp/services/ 2>/dev/null

echo "✅ Ready!"
echo ""
echo "🔴 LIVE NEPSE Stock Dashboard"
echo "Press Ctrl+C to stop"
echo ""

# Run dashboard directly
docker exec airflow-airflow-standalone-1 bash <<'EOF'
export KAFKA_BROKER=kafka:9092
export PYTHONPATH=/tmp:$PYTHONPATH
cd /tmp/streaming/consumers
python3 nepse_dashboard.py compact
EOF
