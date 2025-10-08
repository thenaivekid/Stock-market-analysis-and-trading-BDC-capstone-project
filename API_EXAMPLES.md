# NEPSE Data API - Examples

Quick examples for all API endpoints.

## Base URL
```
http://localhost:8000
```

## Market Data APIs

### Get Live Market Data
```bash
curl "http://localhost:8000/api/market/live"
```

Returns real-time data for all listed stocks with complete information.

### Get Market Summary
```bash
curl "http://localhost:8000/api/market/summary"
```

Response:
```json
{
  "totalStocks": 332,
  "advancing": 180,
  "declining": 120,
  "unchanged": 32,
  "totalTurnover": 5234567890.50,
  "totalVolume": 12500000,
  "totalTransactions": 48523,
  "timestamp": "2025-10-08T14:30:00"
}
```

### Top Gainers
```bash
# Get top 5 gainers
curl "http://localhost:8000/api/market/gainers?limit=5"

# Get top 20 gainers
curl "http://localhost:8000/api/market/gainers?limit=20"
```

### Top Losers
```bash
curl "http://localhost:8000/api/market/losers?limit=10"
```

### Most Active by Volume
```bash
curl "http://localhost:8000/api/market/active/volume?limit=10"
```

Returns stocks with highest trading volume (shares traded).

### Most Active by Value (Turnover)
```bash
curl "http://localhost:8000/api/market/active/value?limit=10"
```

Returns stocks with highest trading value in NPR.

### Most Active by Transactions
```bash
curl "http://localhost:8000/api/market/active/transactions?limit=10"
```

Returns stocks with most number of trades.

### 52-Week High
```bash
curl "http://localhost:8000/api/market/52week/high?limit=10"
```

Returns stocks near or at their 52-week high price.

### 52-Week Low
```bash
curl "http://localhost:8000/api/market/52week/low?limit=10"
```

Returns stocks near or at their 52-week low price.

### Stocks by Sector
```bash
# Commercial Banks
curl "http://localhost:8000/api/market/sector/Commercial%20Banks"

# Hydropower
curl "http://localhost:8000/api/market/sector/Hydropower"

# Development Banks
curl "http://localhost:8000/api/market/sector/Development%20Banks"
```

## Metadata APIs

### Get All Companies
```bash
curl "http://localhost:8000/api/metadata/companies"
```

### Get All Sectors
```bash
curl "http://localhost:8000/api/metadata/sectors"
```

Response:
```json
[
  "Commercial Banks",
  "Development Banks",
  "Finance",
  "Hydropower",
  "Life Insurance",
  "Non Life Insurance",
  ...
]
```

### Update Metadata
```bash
curl -X POST "http://localhost:8000/api/metadata/update"
```

Fetches latest data from NEPSE and updates local metadata.

## Floorsheet API

### Get Floorsheet Data
```bash
curl -X POST "http://localhost:8000/api/floorsheet/" \
  -H "Content-Type: application/json" \
  -d '{"symbol": "NABIL"}'
```

Response:
```json
{
  "symbol": "NABIL",
  "headers": ["Time", "Contract No", "Symbol", "Buyer", "Seller", "Quantity", "Rate", "Amount"],
  "rows": [
    ["10:00:15", "20251008-1", "NABIL", "1234", "5678", "10", "1200.00", "12000.00"],
    ["10:02:30", "20251008-2", "NABIL", "2345", "6789", "25", "1201.00", "30025.00"]
  ]
}
```

## Python Examples

### Using `requests` library

```python
import requests

BASE_URL = "http://localhost:8000"

# Get market summary
response = requests.get(f"{BASE_URL}/api/market/summary")
data = response.json()
print(f"Advancing: {data['advancing']}, Declining: {data['declining']}")

# Get top gainers
response = requests.get(f"{BASE_URL}/api/market/gainers?limit=5")
gainers = response.json()
for stock in gainers:
    print(f"{stock['symbol']}: +{stock['percentageChange']}%")

# Get sector stocks
response = requests.get(f"{BASE_URL}/api/market/sector/Commercial Banks")
banks = response.json()
print(f"Found {len(banks)} commercial banks")

# Scrape floorsheet
response = requests.post(
    f"{BASE_URL}/api/floorsheet/",
    json={"symbol": "NABIL"}
)
floorsheet = response.json()
print(f"Floorsheet rows: {len(floorsheet['rows'])}")
```

## JavaScript/Node.js Examples

```javascript
const BASE_URL = "http://localhost:8000";

// Get market summary
fetch(`${BASE_URL}/api/market/summary`)
  .then(res => res.json())
  .then(data => {
    console.log(`Total stocks: ${data.totalStocks}`);
    console.log(`Turnover: NPR ${data.totalTurnover.toLocaleString()}`);
  });

// Get top losers
fetch(`${BASE_URL}/api/market/losers?limit=5`)
  .then(res => res.json())
  .then(losers => {
    losers.forEach(stock => {
      console.log(`${stock.symbol}: ${stock.percentageChange}%`);
    });
  });

// Get floorsheet
fetch(`${BASE_URL}/api/floorsheet/`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ symbol: 'NABIL' })
})
  .then(res => res.json())
  .then(data => console.log('Floorsheet data:', data));
```

## Interactive API Documentation

Visit **http://localhost:8000/docs** for interactive Swagger UI documentation where you can test all endpoints directly in your browser.

## Rate Limiting & Best Practices

- Live market data endpoints fetch from external APIs - avoid excessive requests
- Floorsheet scraping uses Selenium - can be slow, use sparingly
- Cache responses when possible to reduce load
- Use appropriate `limit` parameters (max 100)
