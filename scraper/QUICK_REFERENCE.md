# NEPSE Data API - Quick Reference

## 🚀 Start Server
```bash
./run.sh
```
Server: http://localhost:8000  
Docs: http://localhost:8000/docs

## 📊 Market Data Endpoints

| Endpoint | Description | Example |
|----------|-------------|---------|
| `GET /api/market/live` | All stocks real-time data | `curl localhost:8000/api/market/live` |
| `GET /api/market/summary` | Market overview stats | `curl localhost:8000/api/market/summary` |
| `GET /api/market/gainers?limit=10` | Top gainers | `curl "localhost:8000/api/market/gainers?limit=5"` |
| `GET /api/market/losers?limit=10` | Top losers | `curl "localhost:8000/api/market/losers?limit=5"` |
| `GET /api/market/active/volume` | Most traded by volume | `curl localhost:8000/api/market/active/volume` |
| `GET /api/market/active/value` | Most traded by value | `curl localhost:8000/api/market/active/value` |
| `GET /api/market/active/transactions` | Most trades count | `curl localhost:8000/api/market/active/transactions` |
| `GET /api/market/52week/high` | Near 52W high | `curl localhost:8000/api/market/52week/high` |
| `GET /api/market/52week/low` | Near 52W low | `curl localhost:8000/api/market/52week/low` |
| `GET /api/market/sector/{name}` | Stocks by sector | `curl "localhost:8000/api/market/sector/Hydropower"` |

## 📁 Metadata Endpoints

| Endpoint | Description |
|----------|-------------|
| `GET /api/metadata/companies` | List all companies |
| `GET /api/metadata/sectors` | List all sectors |
| `POST /api/metadata/update` | Update metadata from live NEPSE |

## 📋 Floorsheet Endpoint

```bash
curl -X POST "http://localhost:8000/api/floorsheet/" \
  -H "Content-Type: application/json" \
  -d '{"symbol": "NABIL"}'
```

## 🧪 Testing

```bash
# Unit tests (in Docker)
docker-compose exec scraper python3 -m unittest discover -s app/tests -v

# Integration tests (from host)
python3 test_integration.py
```

## 📦 Key Data Fields

All market endpoints return stocks with:
- `symbol` - Stock symbol (e.g., "NABIL")
- `securityName` - Full company name
- `sector` - Sector classification
- `lastTradedPrice` - Current price
- `percentageChange` - % change from previous close
- `change` - Absolute price change
- `openPrice` - Opening price
- `highPrice` - Day high
- `lowPrice` - Day low
- `previousClose` - Previous day's closing
- `totalTransactions` - Number of trades
- `totalTradeQuantity` - Total shares traded
- `totalTradeValue` - Total value traded (NPR)
- `lastTradedVolume` - Last trade volume
- `lastUpdatedDateTime` - Last update time

## 🛑 Stop Server
```bash
docker-compose down
```

## 📚 More Info
- Full examples: `API_EXAMPLES.md`
- Complete README: `README.md`
- Test details: `TEST_SUMMARY.md`
- Interactive docs: http://localhost:8000/docs
