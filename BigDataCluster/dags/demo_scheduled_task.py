"""
Demo DAG - Scheduled to run every minute
This will help you understand Airflow scheduling
"""
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator

# Define default arguments
default_args = {
    'owner': 'student',
    'depends_on_past': False,
    'start_date': datetime.now() + timedelta(minutes=2),  # Start 2 min in the future
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(seconds=30),
}

def print_current_time(**context):
    """Print the current execution time"""
    execution_date = context['execution_date']
    logical_date = context['logical_date']
    
    print("=" * 60)
    print(f"🕐 Task executed at: {datetime.now()}")
    print(f"📅 Execution date: {execution_date}")
    print(f"📅 Logical date: {logical_date}")
    print(f"🎯 This is scheduled run!")
    print("=" * 60)
    
    # Simulate some work
    import time
    print("⏳ Processing data...")
    time.sleep(5)
    print("✅ Processing complete!")
    
    return f"Completed at {datetime.now()}"


def check_data_quality(**context):
    """Simulate data quality check"""
    print("🔍 Checking data quality...")
    print("✅ All checks passed!")
    return "Data quality OK"


# Create the DAG
with DAG(
    'demo_every_minute',
    default_args=default_args,
    description='Demo DAG that runs every minute',
    
    # 🔥 THIS IS THE KEY - Schedule to run every minute
    schedule_interval='*/1 * * * *',  # Cron: every 1 minute
    # Alternative: schedule_interval=timedelta(minutes=1)
    
    catchup=True,  # Run missed schedules (for demo purposes)
    max_active_runs=1,  # Only 1 run at a time
    tags=['demo', 'tutorial', 'scheduled'],
) as dag:

    # Task 1: Print start time
    start_task = BashOperator(
        task_id='start',
        bash_command='echo "🚀 Starting scheduled job at $(date)"',
    )

    # Task 2: Execute main logic
    main_task = PythonOperator(
        task_id='print_time',
        python_callable=print_current_time,
        provide_context=True,
    )

    # Task 3: Data quality check
    quality_check = PythonOperator(
        task_id='quality_check',
        python_callable=check_data_quality,
        provide_context=True,
    )

    # Task 4: Print end time
    end_task = BashOperator(
        task_id='end',
        bash_command='echo "✅ Scheduled job completed at $(date)"',
    )

    # Define task dependencies
    start_task >> main_task >> quality_check >> end_task
