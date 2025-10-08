make start-all

make test

# Open Airflow in host browser
"$BROWSER" http://localhost:8090

# Open Spark UI
"$BROWSER" http://localhost:8080

# Open HDFS UI
"$BROWSER" http://localhost:9870

---
## 🎓 NEW: Learn Airflow Scheduling!

Two demo DAGs to learn scheduling:
- `demo_every_minute` - Runs every minute automatically
- `demo_run_in_2_minutes` - Runs once, 2 min after enabling

**Quick Start:**
1. Open Airflow UI (link above)
2. Enable both demo DAGs (toggle ON)
3. Watch them run automatically!

**Full Guide:** See `QUICK_START_SCHEDULING.md` and `SCHEDULING_GUIDE.md`

---
## ✅ ALL ISSUES FIXED! Pipeline Running Successfully!

### Fixed Issues:
1. ✅ Java installation in Airflow container (`openjdk-11-jdk`)
2. ✅ JAVA_HOME path corrected (`/usr/lib/jvm/java-11-openjdk-amd64` not `arm64`)
3. ✅ PySpark version match (3.5.0 matching Spark cluster)
4. ✅ Spark connection (removed YARN, using `spark://spark-spark-1:7077`)
5. ✅ Spark job connects to cluster successfully
6. ✅ Kafka broker running and accessible from Spark worker

### Key Configuration Changes:
- **Airflow Dockerfile**: Fixed JAVA_HOME to `amd64`, added PySpark==3.5.0
- **Spark Connection**: Host=`spark://spark-spark-1`, Port=7077, no extra YARN config
- **DAG**: Added explicit spark.master config
- **Kafka**: Restarted kafka broker (it had stopped)

### Verification:
```bash
# Check all services
docker ps | grep -E "airflow|spark|kafka|hdfs"

# Trigger DAG
docker exec airflow-airflow-standalone-1 airflow dags trigger etl_task

# Check task status
docker exec airflow-airflow-standalone-1 airflow tasks state etl_task spark_job <RUN_ID>
```

### Success Indicators:
- Upload to HDFS: ✅ SUCCESS
- Spark job execution: ✅ SUCCESS  
- Data validation: ✅ Complete
- Output to Kafka: ✅ Complete
- Output to HDFS: ✅ Complete
