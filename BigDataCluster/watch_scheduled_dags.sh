#!/bin/bash
# Watch scheduled DAGs in real-time

echo "📊 Watching Scheduled DAGs..."
echo "Press Ctrl+C to stop"
echo ""

while true; do
    clear
    echo "🕐 Current Time: $(date '+%Y-%m-%d %H:%M:%S')"
    echo "="* 70
    echo ""
    
    echo "📅 DAG Schedules:"
    docker exec airflow-airflow-standalone-1 airflow dags list | grep -E "demo|etl_task" || echo "No demo DAGs found"
    echo ""
    
    echo "🏃 Recent DAG Runs (last 5):"
    docker exec airflow-airflow-standalone-1 airflow dags list-runs -d demo_run_in_2_minutes --state running,success,failed 2>/dev/null | head -6 || echo "DAG not detected yet"
    echo ""
    
    echo "⏰ Next Scheduled Runs:"
    docker exec airflow-airflow-standalone-1 airflow dags next-execution demo_every_minute 2>/dev/null || echo "  demo_every_minute: Not scheduled yet"
    docker exec airflow-airflow-standalone-1 airflow dags next-execution demo_run_in_2_minutes 2>/dev/null || echo "  demo_run_in_2_minutes: Not scheduled yet"
    echo ""
    
    echo "Refreshing in 10 seconds... (Ctrl+C to stop)"
    sleep 10
done
