#!/bin/bash

echo "Starting Selenium Chrome and Scraper containers..."

# Build and start both containers
docker-compose up --build
# If you want to rebuild without using cache, uncomment the following line:
# docker-compose build --no-cache && docker-compose up

# Alternative: Run in detached mode
# docker-compose up --build -d

# To view logs:
# docker-compose logs -f scraper

# To stop:
# docker-compose down