# 🚀 NEPSE Streaming - Quick Start

## ✅ Ready to Use!

All files organized in `/streaming` directory with proper dependencies.

## 🎯 Run It (2 Simple Commands)

### Terminal 1 - Producer:
```bash
cd streaming/scripts
./quick_start.sh producer
```

### Terminal 2 - Dashboard:
```bash
cd streaming/scripts  
./quick_start.sh dashboard
```

## 📊 What You'll See

### Producer:
```
✅ [19:30:45.123] Stocks: 333 | Sent: 3363 msgs | Rate: 336 msg/s | Fetch: 250ms | Actual: 1000ms
```

### Dashboard:
```
📊 MARKET SUMMARY
Total Stocks:     333
🟢 Advancing:     156
🔴 Declining:     142
Total Turnover:   Rs. 2,845,678,901.50

🟢 Top 5 Gainers:
  1. NABIL    | Rs. 1,230.00   | +5.67%
  2. NICA     | Rs. 875.00     | +4.23%
```

## 📦 On New Machine

```bash
git clone repo
cd streaming
pip install -r requirements.txt  # All dependencies here!
./scripts/quick_start.sh
```

## 📚 Full Docs

- `streaming/README.md` - Complete guide
- `CLEAN_ARCHITECTURE.md` - What we fixed
