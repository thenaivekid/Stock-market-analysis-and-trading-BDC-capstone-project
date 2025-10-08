# NEPSE Data API

FastAPI-based scraper and API for Nepal Stock Exchange (NEPSE) data.

## Quick Start

### Run Server

```bash
# Using Docker Compose (recommended)
./run.sh

# Or manually
docker-compose up -d --build
```

Server runs at: **http://localhost:8000**  
API Docs: **http://localhost:8000/docs**

### Run Tests

**Unit Tests (inside Docker):**
```bash
# Run tests in the Docker container
docker-compose exec scraper python3 -m unittest discover -s app/tests -v
```

**Integration Tests (from host):**
```bash
# Test API endpoints from outside Docker (containers must be running)
python3 test_integration.py
```

### Test Results

All 56 unit tests and 15 integration tests pass ✓

## API Endpoints

### Health

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Health check + API info |
| GET | `/health` | Detailed health status |

### Metadata

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/metadata/companies` | List all companies |
| GET | `/api/metadata/sectors` | List all sectors |
| POST | `/api/metadata/update` | Fetch & update metadata from live NEPSE |

### Market Data (Live)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/market/live` | Real-time data for all stocks |
| GET | `/api/market/summary` | Market overview (advancing, declining, turnover, etc.) |
| GET | `/api/market/gainers?limit=10` | Top gaining stocks by % change |
| GET | `/api/market/losers?limit=10` | Top losing stocks by % change |
| GET | `/api/market/active/volume?limit=10` | Most traded stocks by volume |
| GET | `/api/market/active/value?limit=10` | Most traded stocks by value (NPR) |
| GET | `/api/market/active/transactions?limit=10` | Most traded stocks by transaction count |
| GET | `/api/market/52week/high?limit=10` | Stocks near 52-week high |
| GET | `/api/market/52week/low?limit=10` | Stocks near 52-week low |
| GET | `/api/market/sector/{sector_name}` | All stocks in a specific sector |

### Floorsheet (Web Scraping)

| Method | Endpoint | Description | Request Body |
|--------|----------|-------------|--------------|
| POST | `/api/floorsheet/` | Scrape floorsheet data for a stock symbol | `{"symbol": "NABIL"}` |

### News (Web Scraping)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/news/?limit=20&max_pages=3` | Get news from ShareSansar (customizable) |
| GET | `/api/news/latest?limit=10` | Get latest news (first page only) |

**News Parameters:**
- `limit`: Number of news items (1-100 for `/api/news/`, 1-50 for `/api/news/latest`)
- `max_pages`: Maximum pages to scrape (1-10, only for `/api/news/`)

**Example:**
```bash
# Get top 5 gainers
curl "http://localhost:8000/api/market/gainers?limit=5"

# Get market summary
curl "http://localhost:8000/api/market/summary"

# Get latest news
curl "http://localhost:8000/api/news/latest?limit=10"

# Get more news with pagination
curl "http://localhost:8000/api/news/?limit=20&max_pages=2"

# Get all stocks in Commercial Banks sector
curl "http://localhost:8000/api/market/sector/Commercial%20Banks"

# Scrape floorsheet
curl -X POST "http://localhost:8000/api/floorsheet/" \
  -H "Content-Type: application/json" \
  -d '{"symbol": "NABIL"}'
```

**Market Data Response:**
```json
{
  "symbol": "NABIL",
  "securityName": "Nabil Bank Limited",
  "sector": "Commercial Banks",
  "lastTradedPrice": 1200.0,
  "percentageChange": 2.5,
  "change": 30.0,
  "openPrice": 1180.0,
  "highPrice": 1210.0,
  "lowPrice": 1175.0,
  "previousClose": 1170.0,
  "totalTransactions": 542,
  "totalTradeQuantity": 12500.0,
  "totalTradeValue": 15000000.0,
  "lastTradedVolume": 100,
  "lastUpdatedDateTime": "2025-10-08 14:30:00"
}
```

**Floorsheet Response:**
```json
{
  "symbol": "NABIL",
  "headers": ["Time", "Contract No", "Symbol", "Buyer", "Seller", "Quantity", "Rate", "Amount"],
  "rows": [
    ["10:00:00", "12345", "NABIL", "Buyer1", "Seller1", "100", "1200", "120000"]
  ]
}
```

**News Response:**
```json
{
  "count": 2,
  "news": [
    {
      "title": "NEPSE reaches new high",
      "date": "2025-10-08",
      "category": "Market",
      "description": "Nepal Stock Exchange index hits record high",
      "link": "https://www.sharesansar.com/news/nepse-high"
    }
  ]
}
```

## Architecture

```
app/
├── main.py              # FastAPI app entry point
├── api.py               # Metadata endpoints
├── routers/
│   ├── floorsheet.py    # Floorsheet scraping endpoints
│   ├── market.py        # Live market data endpoints
│   └── news.py          # News scraping endpoints
├── services/
│   ├── scraper.py       # Selenium scraping service
│   ├── market_data.py   # Market data fetching & analysis
│   └── news_scraper.py  # News scraping service (BeautifulSoup)
├── tests/               # Unit tests (run in Docker)
│   ├── test_main.py
│   ├── test_floorsheet_router.py
│   ├── test_metadata_api.py
│   ├── test_scraper_service.py
│   ├── test_market_service.py
│   ├── test_market_router.py
│   ├── test_news_scraper.py
│   └── test_news_router.py
└── utils.py             # Helper functions

test_integration.py      # Integration tests (external)
run_tests.sh             # Test runner script
docker-compose.yml       # Container orchestration
Dockerfile              # App container config
```

## Stack

- **FastAPI** - Web framework
- **Selenium** - Web scraping (floorsheet)
- **BeautifulSoup4** - HTML parsing (news)
- **Pandas** - Data processing
- **Docker** - Containerization

## Services

- **scraper** (port 8000) - FastAPI application
- **selenium-chrome** (port 4444) - Headless Chrome for scraping

## Stop Server

```bash
docker-compose down
```
