"""
Special Demo - Runs ONCE at a specific time (2 minutes from now)
Watch this in the Airflow UI!
"""
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator

# Calculate time 2 minutes from now
start_time = datetime.now() + timedelta(minutes=2)

print(f"⏰ This DAG will run at: {start_time.strftime('%H:%M:%S')}")
print(f"⏰ Current time: {datetime.now().strftime('%H:%M:%S')}")
print(f"⏰ Wait approximately 2 minutes and check Airflow UI!")

def celebrate():
    """Celebration function when the scheduled task runs!"""
    print("=" * 70)
    print("🎉🎉🎉 CONGRATULATIONS! 🎉🎉🎉")
    print("=" * 70)
    print(f"✅ Your scheduled task ran successfully at {datetime.now()}")
    print("✅ You now understand Airflow scheduling!")
    print("=" * 70)
    
    print("\n📚 What you learned:")
    print("  1. How to set start_date to schedule future runs")
    print("  2. How to use @once to run exactly one time")
    print("  3. How to monitor scheduled tasks in Airflow UI")
    
    print("\n🎯 Next challenge:")
    print("  Try changing schedule_interval to run every 5 minutes!")
    print("  schedule_interval='*/5 * * * *'")
    print("=" * 70)
    
    return "Success! 🚀"


with DAG(
    'demo_run_in_2_minutes',
    description='Demo that runs once, 2 minutes from now',
    
    # 🔥 KEY: Start time is 2 minutes in the future
    start_date=start_time,
    
    # 🔥 Run only ONCE
    schedule_interval='@once',
    
    catchup=False,
    tags=['demo', 'tutorial', 'timed'],
) as dag:

    # Task 1: Announce start
    announce = BashOperator(
        task_id='announce',
        bash_command=f'echo "🚀 Scheduled task starting at $(date)! This was scheduled for {start_time}"',
    )

    # Task 2: Celebrate
    celebrate_task = PythonOperator(
        task_id='celebrate',
        python_callable=celebrate,
    )

    # Task 3: Finish
    finish = BashOperator(
        task_id='finish',
        bash_command='echo "✅ All done! Check the celebrate task logs for your message!"',
    )

    announce >> celebrate_task >> finish
