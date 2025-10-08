#!/bin/bash
# Run NEPSE streaming components inside Airflow container
# This avoids network issues by running on the Docker network

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
STREAMING_DIR="$PROJECT_ROOT/streaming"
SCRAPER_DIR="$PROJECT_ROOT/scraper/app"

echo "🚀 NEPSE Real-Time Streaming System"
echo "====================================="
echo ""

# Function to copy files to container
copy_files() {
    echo "📦 Copying files to Airflow container..."
    
    # Create directories in /tmp (has write permissions)
    docker exec airflow-airflow-standalone-1 mkdir -p /tmp/streaming/producers /tmp/streaming/consumers /tmp/services
    
    # Copy streaming components
    docker cp "$STREAMING_DIR/producers/nepse_producer.py" airflow-airflow-standalone-1:/tmp/streaming/producers/
    docker cp "$STREAMING_DIR/consumers/nepse_dashboard.py" airflow-airflow-standalone-1:/tmp/streaming/consumers/
    
    # Copy scraper services (dependency)
    docker cp "$SCRAPER_DIR/services/." airflow-airflow-standalone-1:/tmp/services/
    
    echo "✅ Files copied successfully!"
    echo ""
}

# Function to run producer
run_producer() {
    local interval=${1:-1000}
    echo "🚀 Starting NEPSE Producer (${interval}ms interval)..."
    echo "Press Ctrl+C to stop"
    echo ""
    
    docker exec airflow-airflow-standalone-1 bash <<EOF
export KAFKA_BROKER=kafka:9092
export PYTHONPATH=/tmp:\$PYTHONPATH
cd /tmp/streaming/producers
python3 nepse_producer.py $interval
EOF
}

# Function to run dashboard
run_dashboard() {
    local mode=${1:-compact}
    echo "📺 Starting NEPSE Dashboard (${mode} mode)..."
    echo "Press Ctrl+C to stop"
    echo ""
    
    docker exec airflow-airflow-standalone-1 bash <<EOF
export KAFKA_BROKER=kafka:9092
export PYTHONPATH=/tmp:\$PYTHONPATH
cd /tmp/streaming/consumers
python3 nepse_dashboard.py $mode
EOF
}

# Function to show stats
show_stats() {
    echo "📊 Kafka Topic Statistics"
    echo "=========================="
    echo ""
    
    for topic in nepse-live-prices nepse-top-gainers nepse-top-losers nepse-market-summary; do
        echo "Topic: $topic"
        count=$(docker exec kafka kafka-run-class kafka.tools.GetOffsetShell \
            --broker-list localhost:9092 \
            --topic "$topic" 2>/dev/null | awk -F':' '{sum+=$3} END {print sum}')
        echo "  Messages: ${count:-0}"
        echo ""
    done
}

# Main menu
show_menu() {
    echo "Choose what to run:"
    echo "  1) Producer (stream stocks to Kafka)"
    echo "  2) Dashboard (display real-time data)"
    echo "  3) Show Kafka statistics"
    echo "  4) Exit"
    echo ""
}

# Copy files first
copy_files

# Interactive menu
while true; do
    show_menu
    read -p "Enter choice (1-4): " choice
    
    case $choice in
        1)
            run_producer 1000
            ;;
        2)
            run_dashboard compact
            ;;
        3)
            show_stats
            ;;
        4)
            echo "Goodbye!"
            exit 0
            ;;
        *)
            echo "Invalid choice!"
            ;;
    esac
    
    echo ""
done
