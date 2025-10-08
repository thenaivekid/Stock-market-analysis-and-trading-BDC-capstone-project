# 🔧 Fixes Applied to BigDataCluster

## Summary
Successfully debugged and fixed the Spark ETL pipeline. All services now running correctly with end-to-end data processing working.

## Issues Fixed

### 1. Java Path Issue ❌→✅
**Problem:** Airflow Dockerfile had wrong JAVA_HOME path
```
ENV JAVA_HOME /usr/lib/jvm/java-11-openjdk-arm64  ❌
```

**Solution:**
```dockerfile
ENV JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64  ✅
ENV PATH="${JAVA_HOME}/bin:${PATH}"
```

**File:** `BigDataCluster/infra/airflow/Dockerfile`

---

### 2. PySpark Version Mismatch ❌→✅
**Problem:** PySpark in Airflow (3.5.7) didn't match Spark cluster (3.5.0)
- Caused: `java.io.InvalidClassException` serialization errors

**Solution:** Pinned PySpark to exact version
```
pyspark==3.5.0
```

**File:** `BigDataCluster/infra/airflow/requirements.txt`

---

### 3. Spark Connection Using YARN ❌→✅
**Problem:** Default Spark connection used YARN mode
```json
{
  "host": "yarn",
  "extra": "{\"queue\": \"root.default\"}"
}
```

**Solution:** Updated to Spark Standalone mode
```bash
airflow connections add spark_default \
  --conn-type spark \
  --conn-host spark://spark-spark-1 \
  --conn-port 7077 \
  --conn-extra '{}'
```

---

### 4. Kafka Broker Not Running ❌→✅
**Problem:** Kafka container had exited
```
CONTAINER ID   STATUS
0520e1eb0a42   Exited (1) About an hour ago
```

**Solution:** Restarted Kafka
```bash
make start-kafka
```

---

### 5. DAG Configuration ❌→✅
**Problem:** SparkSubmitOperator missing explicit master configuration

**Solution:** Added conf parameter
```python
spark_job = SparkSubmitOperator(
    task_id='spark_job',
    conn_id='spark_default',
    application="/opt/airflow/dags/pipelines/etl.py",
    conf={
        'spark.master': 'spark://spark-spark-1:7077'
    },
    packages='org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0',
    verbose=True
)
```

**File:** `BigDataCluster/dags/task.py`

---

## Verification Steps

### 1. Check All Services Running
```bash
docker ps --format "table {{.Names}}\t{{.Status}}"
```

Expected output:
```
kafka                          Up
kafka-zookeeper-1              Up  
spark-spark-1                  Up
spark-spark-worker-1           Up
namenode                       Up (healthy)
datanode                       Up (healthy)
airflow-airflow-standalone-1   Up
```

### 2. Verify PySpark Version Match
```bash
# Airflow
docker exec airflow-airflow-standalone-1 python -c "import pyspark; print(pyspark.__version__)"
# Output: 3.5.0

# Spark Cluster
docker exec spark-spark-1 /opt/spark/bin/spark-submit --version 2>&1 | grep version
# Output: version 3.5.0
```

### 3. Test Spark Connection
```bash
docker exec airflow-airflow-standalone-1 nc -zv spark-spark-1 7077
# Output: Connection to spark-spark-1 (IP) 7077 port [tcp/*] succeeded!
```

### 4. Test Kafka Connection from Spark Worker
```bash
docker exec spark-spark-worker-1 sh -c 'getent hosts kafka'
# Output: 172.18.0.X      kafka
```

### 5. Run ETL Pipeline
```bash
docker exec airflow-airflow-standalone-1 airflow dags trigger etl_task
sleep 60
docker exec airflow-airflow-standalone-1 airflow tasks state etl_task spark_job <RUN_ID>
# Output: success ✅
```

---

## Files Modified

1. `BigDataCluster/infra/airflow/Dockerfile` - Fixed JAVA_HOME
2. `BigDataCluster/infra/airflow/requirements.txt` - Pinned PySpark version  
3. `BigDataCluster/dags/task.py` - Added explicit Spark master config
4. `BigDataCluster/run.md` - Updated with success status

---

## Lessons Learned

1. **Version Matching**: Always ensure client/server versions match exactly (PySpark ↔ Spark)
2. **Network Configuration**: All services must be on same Docker network for hostname resolution
3. **Connection Management**: Airflow connections can have hidden defaults (like YARN mode)
4. **Service Health**: Check all dependent services are running before troubleshooting application logic
5. **Logging**: Always check logs in order: Airflow → Spark Master → Spark Worker → Application

---

## Quick Start (After Fixes)

```bash
cd BigDataCluster

# Start all services
make start-all

# Wait for services to be ready (30 seconds)
sleep 30

# Verify services
docker ps | grep -E "airflow|spark|kafka|hdfs"

# Trigger DAG
docker exec airflow-airflow-standalone-1 airflow dags trigger etl_task

# Check status
docker exec airflow-airflow-standalone-1 airflow dags list-runs -d etl_task --state success
```

---

## Architecture Overview

```
┌─────────────┐
│   Airflow   │ (Orchestrator)
│  :8090      │
└──────┬──────┘
       │ triggers
       ↓
┌─────────────┐     ┌──────────────┐
│    HDFS     │────→│ Spark Master │
│  :9870      │     │    :8080     │
└─────────────┘     └──────┬───────┘
                           │ distributes work
                           ↓
                    ┌──────────────┐
                    │ Spark Worker │
                    └──────┬───────┘
                           │ writes to
                           ↓
                    ┌──────────────┐
                    │    Kafka     │
                    │    :9092     │
                    └──────────────┘
```

---

## Success! 🎉

All ETL pipeline components are now working:
- ✅ Data ingestion from HDFS
- ✅ Distributed processing with Spark
- ✅ Data validation and transformation
- ✅ Output to Kafka for streaming
- ✅ Output to HDFS for batch storage
- ✅ Orchestration with Airflow

