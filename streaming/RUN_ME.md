# 🚀 NEPSE Live Streaming - Super Simple Guide

## Two Simple Commands (No Prompts!)

### Terminal 1 - Start Producer (100ms real-time streaming):
```bash
cd streaming/scripts
./producer.sh 100
```

### Terminal 2 - Watch Live Dashboard:
```bash
cd streaming/scripts
./dashboard.sh
```

That's it! 🎉

## What You'll See:

### Dashboard Output (Real-Time Updates):
```
⏰ 19:45:30 - Live Update
📊 MARKET SUMMARY
======================================================================
Total Stocks:     333
🟢 Advancing:     156 (stocks going UP)
🔴 Declining:     142 (stocks going DOWN)
⚪ Unchanged:     35
Total Turnover:   Rs. 2,845,678,901.50
Total Volume:     45,678,234
Total Trades:     123,456

🟢 Top 5 Gainers (Prices INCREASING):
  1. NABIL    | Rs. 1,230.00   | +5.67%  ⬆️
  2. NICA     | Rs. 875.00     | +4.23%  ⬆️
  3. SCB      | Rs. 450.00     | +3.89%  ⬆️
  4. EBL      | Rs. 650.00     | +3.45%  ⬆️
  5. ADBL     | Rs. 320.00     | +2.98%  ⬆️

🔴 Top 5 Losers (Prices DECREASING):
  1. XYZ      | Rs. 120.00     | -4.56%  ⬇️
  2. ABC      | Rs. 250.00     | -3.78%  ⬇️
  3. DEF      | Rs. 180.00     | -2.99%  ⬇️
  4. GHI      | Rs. 340.00     | -2.45%  ⬇️
  5. JKL      | Rs. 190.00     | -1.89%  ⬇️

----------------------------------------------------------------------
📊 Messages received: 3,695 (and counting...)
----------------------------------------------------------------------

⏰ 19:45:35 - Live Update  (← Updates every 5 seconds!)
📊 MARKET SUMMARY
... (new data shows price changes!)
```

### Producer Output:
```
✅ [19:45:30.123] Stocks: 333 | Sent: 3,363 msgs | Rate: 336 msg/s | Fetch: 250ms
✅ [19:45:30.523] Stocks: 333 | Sent: 6,726 msgs | Rate: 336 msg/s | Fetch: 245ms
... (streams every 100ms)
```

## 🔥 Watch Prices Change Live!

Every 5 seconds the dashboard updates with:
- **New stock prices** from the live API
- **Updated gainers/losers** rankings
- **Fresh market statistics**

You'll literally see prices changing in real-time! 📈📉

## Stop Streaming:
Press **Ctrl+C** in both terminals

## Change Update Speed:
```bash
# Super fast - 100ms (default)
./producer.sh 100

# Medium - 500ms
./producer.sh 500

# Slow - 2 seconds
./producer.sh 2000
```
