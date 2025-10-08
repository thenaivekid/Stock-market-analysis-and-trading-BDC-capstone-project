# 🎯 Quick Start - See Scheduling in Action!

## ⚡ What We Created

Two demo DAGs to teach you scheduling:

1. **`demo_every_minute`** - Runs automatically every minute
2. **`demo_run_in_2_minutes`** - Runs once, 2 minutes after you enable it

---

## 🚀 5-Minute Tutorial

### Step 1: Open Airflow (30 seconds)

```bash
"$BROWSER" http://localhost:8090
```

Login: `admin` / `admin`

### Step 2: Enable the DAGs (1 minute)

1. Look for **`demo_every_minute`** in the DAGs list
2. Click the **toggle slider** (left side) to turn it **ON** (blue)
3. Do the same for **`demo_run_in_2_minutes`**

### Step 3: Watch Magic Happen! (3 minutes)

**What you'll see:**

#### For `demo_every_minute`:
- ⏰ Runs automatically **every 60 seconds**
- 📊 Click DAG name → Graph view to see tasks execute
- 🟢 Tasks turn: ⚪ white → 🟡 yellow → 🟢 green
- 📈 Tree view shows multiple runs stacking up

#### For `demo_run_in_2_minutes`:
- ⏰ Waits 2 minutes, then runs **exactly once**
- 🎉 Click on `celebrate` task → Logs → See congratulations message!
- ✅ After running, it stops (won't run again)

---

## 🎓 What Each Task Does

### `demo_every_minute` Tasks:

```
start → print_time → quality_check → end
```

- **start**: Prints start timestamp
- **print_time**: Shows current time and execution date
- **quality_check**: Simulates data validation
- **end**: Prints completion timestamp

### `demo_run_in_2_minutes` Tasks:

```
announce → celebrate → finish
```

- **announce**: Announces the scheduled run
- **celebrate**: Prints congratulations message (check logs!)
- **finish**: Marks completion

---

## 📊 Monitoring Commands

### Check Next Run Time
```bash
docker exec airflow-airflow-standalone-1 \
  airflow dags next-execution demo_every_minute
```

### List Recent Runs
```bash
docker exec airflow-airflow-standalone-1 \
  airflow dags list-runs -d demo_every_minute
```

### Check DAG Status
```bash
docker exec airflow-airflow-standalone-1 \
  airflow dags state demo_every_minute
```

---

## 🎯 Experiment Time!

### Challenge 1: Change the Schedule

Edit `demo_every_minute` to run every 5 minutes instead:

1. Open: `BigDataCluster/dags/demo_scheduled_task.py`
2. Find: `schedule_interval='*/1 * * * *'`
3. Change to: `schedule_interval='*/5 * * * *'`
4. Save file
5. Wait 30 seconds for Airflow to detect change
6. Watch it run every 5 minutes!

### Challenge 2: Schedule Your ETL

Make `etl_task` run every day at 2 AM:

1. Open: `BigDataCluster/dags/task.py`
2. Find: `schedule_interval=None`
3. Change to: `schedule_interval='0 2 * * *'`
4. Save and enable DAG
5. It will run daily at 2:00 AM!

---

## 🕐 Schedule Cheat Sheet

| What | Cron Expression | Description |
|------|----------------|-------------|
| Every minute | `* * * * *` | For testing |
| Every 5 min | `*/5 * * * *` | Real-time data |
| Every 15 min | `*/15 * * * *` | Frequent updates |
| Every hour | `0 * * * *` | Hourly jobs |
| Every 6 hours | `0 */6 * * *` | Periodic sync |
| Daily 2 AM | `0 2 * * *` | Nightly ETL |
| Daily 9 AM | `0 9 * * *` | Morning reports |
| Monday 9 AM | `0 9 * * 1` | Weekly reports |
| 1st of month | `0 0 1 * *` | Monthly reports |
| Twice daily | `0 6,18 * * *` | 6 AM and 6 PM |

---

## 🐛 Troubleshooting

### DAG not running?

**✓ Check 1:** Is the toggle **ON** (blue)?
- Go to DAGs list
- Look at the slider on the left
- Should be blue/enabled

**✓ Check 2:** Is start_date in the past?
```python
# ❌ Wrong - too far in future
start_date=datetime(2026, 1, 1)

# ✅ Correct - recent past
start_date=datetime.now() - timedelta(hours=1)
```

**✓ Check 3:** Is scheduler running?
```bash
docker exec airflow-airflow-standalone-1 ps aux | grep scheduler
```

### Not seeing runs?

```python
catchup=False  # Add this to skip historical runs
```

---

## 📚 Learn More

Full guide: `BigDataCluster/SCHEDULING_GUIDE.md`

Topics covered:
- ✅ Cron expressions in detail
- ✅ Timedelta scheduling
- ✅ Advanced scheduling patterns
- ✅ SLA monitoring
- ✅ Email alerts
- ✅ Sensors and dependencies

---

## 🎉 Success Checklist

After completing this tutorial, you should:

- [ ] See `demo_every_minute` running automatically
- [ ] See multiple runs in Tree view
- [ ] Read the "celebrate" task logs
- [ ] Understand cron syntax
- [ ] Know how to enable/disable DAGs
- [ ] Be able to schedule your own tasks

**Congratulations! You now understand Airflow scheduling!** 🚀

---

## 🚀 Next Steps

1. **Try different schedules** - Experiment with cron expressions
2. **Schedule your scraper** - Run stock data collection every 5 minutes
3. **Create reports** - Schedule weekly or monthly reports
4. **Set up alerts** - Get notified when tasks fail

Need help? Check `SCHEDULING_GUIDE.md` or ask! 😊
