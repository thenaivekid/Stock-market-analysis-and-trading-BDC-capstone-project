"""
Demo: Fastest Practical Airflow Schedule
Runs every 1 minute (shortest recommended interval)

NOTE: 100ms is NOT possible with Airflow!
For sub-second tasks, use Kafka consumers or async Python scripts.
"""
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
import time

def fast_task():
    """A quick task that simulates fast processing"""
    start = time.time()
    
    print("=" * 70)
    print(f"⚡ FAST TASK EXECUTING at {datetime.now().strftime('%H:%M:%S.%f')[:-3]}")
    print("=" * 70)
    
    # Simulate quick work (100ms)
    time.sleep(0.1)
    
    end = time.time()
    print(f"✅ Task completed in {(end - start)*1000:.2f} milliseconds")
    print(f"⏰ Next run in 60 seconds (Airflow minimum practical interval)")
    print("=" * 70)
    
    return f"Success at {datetime.now()}"


with DAG(
    'hey_run',
    description='Fastest practical Airflow schedule - every 1 minute',
    
    # Every 1 minute (fastest practical interval)
    schedule_interval='*/1 * * * *',

    start_date=datetime.now() - timedelta(minutes=1),
    catchup=True,  # Don't run past intervals
    max_active_runs=1,  # Only 1 run at a time
    tags=['demo', 'fast', 'tutorial'],
) as dag:

    # Quick task
    fast_execution = PythonOperator(
        task_id='fast_task',
        python_callable=fast_task,
    )

    # Show timestamp
    timestamp = BashOperator(
        task_id='show_timestamp',
        bash_command='echo "Executed at: $(date +%H:%M:%S.%N | cut -b1-12)"',
    )

    fast_execution >> timestamp


# Educational notes printed when DAG loads
print("📚 IMPORTANT: Airflow Scheduling Limits")
print("=" * 70)
print("✅ Minimum practical interval: 1 minute (*/1 * * * *)")
print("❌ Sub-second (100ms) intervals: NOT SUPPORTED")
print("")
print("For 100ms intervals, use:")
print("  - Kafka consumers (already in your stack!)")
print("  - Python asyncio loops")
print("  - Celery beat")
print("  - Apache Flink")
print("=" * 70)
