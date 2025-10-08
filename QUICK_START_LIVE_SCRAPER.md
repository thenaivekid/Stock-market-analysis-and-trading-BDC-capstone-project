# 🚀 Quick Start - NEPSE Live Scraper

## Run Everything in One Command

```bash
./start_live_scraper.sh
```

That's it! This script will:
1. ✅ Start all Docker containers (Kafka, Airflow, etc.)
2. ✅ Copy streaming files to container
3. ✅ Install dependencies
4. ✅ Start NEPSE producer (scraping every 100ms)
5. ✅ Show live dashboard with real-time stock prices

## What You'll See

The dashboard will show:
- 📊 Market summary (total stocks, gainers, losers)
- 📈 Top gainers (stocks going up)
- 📉 Top losers (stocks going down)
- 🔄 Updates every 5 seconds

Press **Ctrl+C** to stop the dashboard.

## If Containers Are Already Running

If your Docker containers are already up, you can skip the startup and just run the scraper:

```bash
# Quick run (containers already running)
cd streaming/scripts
./producer.sh 100    # In terminal 1
./dashboard.sh       # In terminal 2
```

## Technical Details

- **Producer**: Fetches NEPSE API every 100ms, streams to Kafka
- **Kafka Topics**: 
  - `nepse-live-prices` - All stock prices
  - `nepse-top-gainers` - Top 10 gainers
  - `nepse-top-losers` - Top 10 losers
  - `nepse-market-summary` - Market overview
- **Dashboard**: Real-time consumer showing live price changes

## Files

- `start_live_scraper.sh` - Main launcher script
- `streaming/producers/nepse_producer.py` - Producer that scrapes NEPSE
- `streaming/consumers/nepse_dashboard.py` - Dashboard consumer
- `docker-compose.yml` - All services configuration
