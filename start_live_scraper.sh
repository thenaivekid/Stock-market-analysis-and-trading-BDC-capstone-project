#!/bin/bash

# NEPSE Live Scraper - Quick Start Script
# This script starts all necessary containers and runs the live NEPSE stock scraper

set -e

echo "🚀 Starting NEPSE Live Scraper System..."
echo ""

# # Step 1: Start all Docker containers
# echo "📦 Starting Docker containers..."
# cd BigDataCluster
# make start-all
# echo ""
# echo "⏳ Waiting for services to be ready (15 seconds)..."
# cd ../
# sleep 15


# Step 2: Copy streaming files to Airflow container
echo ""
echo "📁 Copying streaming files to container..."
docker cp streaming/producers airflow-airflow-standalone-1:/tmp/streaming/
docker cp streaming/consumers airflow-airflow-standalone-1:/tmp/streaming/
docker cp scraper/app/services airflow-airflow-standalone-1:/tmp/

echo ""
echo "✅ Files copied successfully!"

# Step 3: Install dependencies in container if needed
echo ""
echo "📦 Installing dependencies in container..."
docker exec airflow-airflow-standalone-1 bash -c 'pip install -q kafka-python requests 2>/dev/null || true'

# Step 4: Start the producer
echo ""
echo "🔴 Starting NEPSE Live Producer (100ms interval)..."
echo ""

# Run producer in background
docker exec -it airflow-airflow-standalone-1 bash -lc "export KAFKA_BROKER=kafka:9092 && export PYTHONPATH=/tmp && cd /tmp/streaming/producers && python3 nepse_producer.py 1000"
sleep 3

# Step 5: Start the dashboard
echo "📊 Starting Live Dashboard..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Run dashboard in foreground (interactive)
docker exec -it airflow-airflow-standalone-1 bash -c \
  'export KAFKA_BROKER=kafka:9092 && export PYTHONPATH=/tmp && cd /tmp/streaming/consumers && python3 nepse_dashboard.py compact'

echo ""
echo "👋 Dashboard stopped."
