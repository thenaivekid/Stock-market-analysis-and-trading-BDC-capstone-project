# 📅 Airflow Scheduling Guide

## 🎯 What You Just Created

A DAG that runs **EVERY MINUTE** automatically!

---

## 🚀 Quick Start - See It Running!

### Step 1: Open Airflow UI
```bash
"$BROWSER" http://localhost:8090
```
Login: `admin` / `admin`

### Step 2: Enable the DAG
1. Look for **`demo_every_minute`** in the DAGs list
2. Click the **toggle switch** on the left (turn it ON/blue)
3. Watch it run automatically!

### Step 3: Watch It Execute
- The DAG will run **every minute**
- Click on the DAG name to see the Graph view
- Watch tasks turn from white → yellow → green
- Check the **Tree View** to see multiple runs over time

---

## 📖 Schedule Syntax Explained

### **Method 1: Cron Expression** (Most Flexible)

```python
schedule_interval='*/1 * * * *'  # Every 1 minute
```

**Cron Format:** `minute hour day month day_of_week`

```
 ┌─────────── minute (0-59)
 │ ┌───────── hour (0-23)
 │ │ ┌─────── day of month (1-31)
 │ │ │ ┌───── month (1-12)
 │ │ │ │ ┌─── day of week (0-6, 0=Sunday)
 │ │ │ │ │
 * * * * *
```

### **Common Cron Examples:**

```python
# Every minute
schedule_interval='* * * * *'

# Every 5 minutes
schedule_interval='*/5 * * * *'

# Every hour at minute 0
schedule_interval='0 * * * *'

# Every day at 2:30 AM
schedule_interval='30 2 * * *'

# Every Monday at 9:00 AM
schedule_interval='0 9 * * 1'

# Every 1st of the month at midnight
schedule_interval='0 0 1 * *'

# Every weekday (Mon-Fri) at 6:00 PM
schedule_interval='0 18 * * 1-5'

# Twice a day (6 AM and 6 PM)
schedule_interval='0 6,18 * * *'
```

### **Method 2: Timedelta** (Simple Intervals)

```python
from datetime import timedelta

# Every 1 minute
schedule_interval=timedelta(minutes=1)

# Every 30 minutes
schedule_interval=timedelta(minutes=30)

# Every 2 hours
schedule_interval=timedelta(hours=2)

# Every day
schedule_interval=timedelta(days=1)

# Every week
schedule_interval=timedelta(weeks=1)
```

### **Method 3: Airflow Presets** (Built-in)

```python
# No schedule (manual only)
schedule_interval=None

# Every minute
schedule_interval='@once'  # Run once then stop

# Daily at midnight
schedule_interval='@daily'    # Same as: '0 0 * * *'

# Weekly on Sunday at midnight
schedule_interval='@weekly'   # Same as: '0 0 * * 0'

# Monthly on 1st at midnight
schedule_interval='@monthly'  # Same as: '0 0 1 * *'

# Yearly on Jan 1st at midnight
schedule_interval='@yearly'   # Same as: '0 0 1 1 *'

# Every hour
schedule_interval='@hourly'   # Same as: '0 * * * *'
```

---

## 🎯 Real-World Examples

### **Example 1: Stock Market Data (Every 5 Minutes During Trading Hours)**

```python
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator

def fetch_stock_prices():
    """Fetch latest stock prices"""
    print("📈 Fetching stock prices...")
    # Your scraper code here
    pass

with DAG(
    'stock_price_fetcher',
    start_date=datetime(2025, 1, 1),
    schedule_interval='*/5 * * * *',  # Every 5 minutes
    catchup=False,
    tags=['stock', 'realtime'],
) as dag:
    
    fetch_task = PythonOperator(
        task_id='fetch_prices',
        python_callable=fetch_stock_prices,
    )
```

### **Example 2: Daily ETL Pipeline (2:00 AM Every Day)**

```python
with DAG(
    'daily_etl_pipeline',
    start_date=datetime(2025, 1, 1),
    schedule_interval='0 2 * * *',  # 2:00 AM daily
    catchup=False,
) as dag:
    
    extract = PythonOperator(task_id='extract', ...)
    transform = PythonOperator(task_id='transform', ...)
    load = PythonOperator(task_id='load', ...)
    
    extract >> transform >> load
```

### **Example 3: Weekly Report (Every Monday 9 AM)**

```python
with DAG(
    'weekly_report',
    start_date=datetime(2025, 1, 1),
    schedule_interval='0 9 * * 1',  # Monday 9 AM
    catchup=False,
) as dag:
    
    generate_report = PythonOperator(task_id='generate', ...)
    send_email = PythonOperator(task_id='email', ...)
    
    generate_report >> send_email
```

---

## ⏰ Understanding Start Date vs Execution Date

### **Key Concepts:**

```python
start_date = datetime(2025, 10, 8, 18, 0, 0)  # When DAG becomes active
schedule_interval = timedelta(minutes=1)       # How often to run
```

**Timeline:**
```
18:00:00 - start_date (DAG becomes active)
18:01:00 - First execution (data from 18:00-18:01)
18:02:00 - Second execution (data from 18:01-18:02)
18:03:00 - Third execution (data from 18:02-18:03)
```

**Important:** Airflow runs at the **END** of the interval!
- `execution_date` = START of interval
- Actual run time = END of interval

---

## 🔧 Important Parameters

### **catchup** (Should I run missed schedules?)

```python
# Scenario: DAG was off for 2 hours, you turn it on

catchup=True   # ✅ Run all 120 missed runs (if interval=1min)
catchup=False  # ❌ Skip missed runs, start fresh
```

**Best practice:** Use `False` for real-time data, `True` for historical processing

### **max_active_runs** (How many runs at once?)

```python
max_active_runs=1   # Only 1 run at a time (wait for previous)
max_active_runs=3   # Allow 3 concurrent runs
```

### **depends_on_past** (Should I wait for previous run?)

```python
depends_on_past=True   # Don't start if previous run failed
depends_on_past=False  # Run regardless of previous status
```

---

## 🎓 Practical Exercise: Schedule Your Stock Market DAG

Let's update your `etl_task` to run every 30 minutes:

```python
with DAG(
    'etl_task',
    description='DAG that executes the ETL pipeline',
    
    # 🔥 CHANGE THIS:
    schedule_interval='*/30 * * * *',  # Every 30 minutes
    # OR: schedule_interval=timedelta(minutes=30)
    
    start_date=datetime(2025, 10, 8, 18, 0, 0),  # Start today at 6 PM
    catchup=False,  # Don't run historical
    max_active_runs=1,  # One at a time
) as dag:
```

---

## 📊 Monitoring Scheduled DAGs

### **Via UI:**

1. **DAGs List Page:**
   - See "Next Run" column
   - See "Last Run" status
   - Recent tasks show as colored boxes

2. **Graph View:**
   - Click on DAG → See visual flow
   - Click on task → See logs

3. **Tree View:**
   - See all historical runs
   - Identify patterns of success/failure

4. **Calendar View:**
   - Heat map of runs by date
   - Quickly spot problem days

### **Via CLI:**

```bash
# List next run times
docker exec airflow-airflow-standalone-1 airflow dags next-execution demo_every_minute

# Check DAG status
docker exec airflow-airflow-standalone-1 airflow dags state demo_every_minute

# List recent runs
docker exec airflow-airflow-standalone-1 airflow dags list-runs -d demo_every_minute --state success
```

---

## 🐛 Troubleshooting

### **DAG not running on schedule?**

1. **Check if DAG is ON (blue toggle)**
   - Go to DAGs list
   - Toggle must be blue/enabled

2. **Check start_date**
   ```python
   # ❌ WRONG - in the future
   start_date=datetime(2026, 1, 1)
   
   # ✅ CORRECT - in the past
   start_date=datetime(2025, 1, 1)
   ```

3. **Check scheduler is running**
   ```bash
   docker exec airflow-airflow-standalone-1 ps aux | grep scheduler
   ```

4. **Check for errors**
   ```bash
   docker logs airflow-airflow-standalone-1 | grep ERROR
   ```

### **Too many runs at once?**

```python
max_active_runs=1  # Limit to 1 concurrent run
```

### **Missing runs when DAG was off?**

```python
catchup=False  # Skip missed runs
```

---

## 🎯 Your Mission

1. ✅ **Enable `demo_every_minute`** - Watch it run automatically
2. ✅ **Check Tree View** - See multiple runs over time
3. ✅ **Create your own** - Schedule a task for 5 minutes from now
4. ✅ **Update `etl_task`** - Schedule it to run daily at 2 AM

---

## 📝 Quick Reference Card

| Schedule | Cron | Timedelta | Use Case |
|----------|------|-----------|----------|
| Every minute | `* * * * *` | `timedelta(minutes=1)` | Testing |
| Every 5 min | `*/5 * * * *` | `timedelta(minutes=5)` | Real-time data |
| Hourly | `0 * * * *` | `timedelta(hours=1)` | Frequent updates |
| Daily 2 AM | `0 2 * * *` | N/A | Nightly ETL |
| Weekdays 6 PM | `0 18 * * 1-5` | N/A | Business hours |
| Monthly | `0 0 1 * *` | N/A | Reports |

---

## 🚀 Next Steps

Want to learn:
- ⏰ **SLA Monitoring** - Alert when tasks take too long
- 📧 **Email Alerts** - Get notified on failures
- 🔄 **Sensors** - Wait for external conditions
- 🎯 **Dynamic DAGs** - Generate DAGs from config files

Just ask! 🎓
