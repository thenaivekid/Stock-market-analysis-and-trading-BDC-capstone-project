#!/bin/bash
# Quick Start Script for NEPSE Streaming
# Usage: ./quick_start.sh [producer|dashboard|docker]

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MODE="${1:-menu}"

case $MODE in
    producer)
        echo "🚀 Starting Producer..."
        bash "$SCRIPT_DIR/run_in_container.sh" <<< "1"
        ;;
    
    dashboard)
        echo "📺 Starting Dashboard..."
        bash "$SCRIPT_DIR/run_in_container.sh" <<< "2"
        ;;
    
    docker)
        echo "🐳 Starting with Docker Compose..."
        cd "$SCRIPT_DIR/../docker"
        docker-compose up -d
        echo "✅ Services started!"
        echo "View logs: docker-compose -f $SCRIPT_DIR/../docker/docker-compose.yml logs -f"
        ;;
    
    *)
        bash "$SCRIPT_DIR/run_in_container.sh"
        ;;
esac
