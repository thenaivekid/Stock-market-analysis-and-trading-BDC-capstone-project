# Run nb

if docker compose is installed as a plug in not as standalone binary do this
-  1️⃣ Download the latest stable docker-compose binary
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
docker-compose --version
- if some other process is using the port used by my continers stop those processes as well

### 1. Start the Big Data Infrastructure
```bash
# Navigate to BigDataCluster directory
cd BigDataCluster

# Start all services (Spark, HDFS, Kafka, Airflow)
make start-all

# Wait for services to be ready (about 30 seconds)
sleep 30
```

### 2. Set Up Jupyter Server
```bash
# Remove any existing Jupyter container
# Remove any existing container
docker rm -f jupyter-spark 2>/dev/null

# Run the Jupyter PySpark container with Python 3.8.8
docker run -d \
  --network custom_network \
  -p 8888:8888 \
  --name jupyter-spark \
  jupyter/pyspark-notebook:python-3.8.8

# Wait a few seconds for the notebook to start
sleep 15

# Get the Jupyter server URL and token
docker exec jupyter-spark jupyter notebook list

docker exec jupyter-spark pip install hdfs
```

### 3. Access Jupyter Notebook
1. Copy the token from the output of the last command
2. Open in browser: http://localhost:8888
3. Enter the token when prompted

### 5. Stop Services
```bash
# When done, stop all services
cd BigDataCluster
make stop-all

# Stop Jupyter container
docker rm -f jupyter-spark
```

---
# what next?

## Architecture Discussion

### Current Setup Analysis:

- **Kafka**: Streaming data source (GLH stock every minute)
- **Spark**: Distributed processing (master + worker)
- **HDFS**: Distributed storage (namenode + datanode)
- **Jupyter-Spark**: Interactive development environment
- **Airflow**: Workflow orchestration

### Recommended Approach:

**1. Spark Structured Streaming Consumer** (Best fit for your setup)

- Runs in the Spark container
- Consumes from Kafka topic
- Loads LSTM model from HDFS
- Makes predictions in real-time
- Writes to HDFS in micro-batches (parquet format)
- Can be deployed as a standalone application or scheduled via Airflow

**2. Data Flow:**
```
Kafka (GLH data) 
  → Spark Structured Streaming
  → Load LSTM Model from HDFS
  → Predict & Generate Trading Signals
  → Write to HDFS (parquet)
  → Separate batch job reads 10-min intervals for pattern analysis
```

**3. Storage Strategy:**
```
HDFS Structure:
/stock_data/
  ├── streaming/           # Real-time data from Kafka
  │   └── GLH/
  │       └── date=2025-11-17/
  │           └── *.parquet
  ├── signals/             # Trading signals
  │   └── GLH/
  │       └── date=2025-11-17/
  │           └── *.parquet
  └── models/              # Your existing models
      └── lstm/
          └── GLH/
```

### Key Design Decisions:

**Q1: Should pattern analysis (Fibonacci) run in the same streaming job?**

- **No** - Keep streaming job focused on ingestion + LSTM predictions
- Pattern analysis should be a separate scheduled job (every 10 min via Airflow)
- Reads accumulated data from HDFS, performs analysis, generates signals

**Q2: Where should the model inference happen?**

- **In Spark streaming job** - Load model once at startup, reuse for predictions
- PyTorch model can run on Spark workers

**Q3: How to handle the "profitable point" logic?**

- Define threshold strategy (e.g., predicted price > current price by X%)
- Implement risk management rules
- Store signals with confidence scores

### Proposed Implementation:

1. **Streaming Application** (`streaming/consumers/trading_stream.py`):
    
    - Consumes Kafka → Predicts → Writes to HDFS
    - Runs continuously in Spark container
2. **Pattern Analysis DAG** (`BigDataCluster/dags/pipelines/pattern_analysis.py`):
    
    - Scheduled every 10 minutes in Airflow
    - Reads 10-min windows from HDFS
    - Fibonacci/pattern detection
    - Generates additional signals
3. **Signal Aggregator** (Optional):
    
    - Combines LSTM + pattern signals
    - Final buy/sell decisions

### Benefits:

- ✅ Separation of concerns (real-time vs batch)
- ✅ Scalable (Spark handles load)
- ✅ Fault-tolerant (Kafka checkpointing, HDFS replication)
- ✅ Replayable (all data in HDFS)
- ✅ Orchestrated (Airflow manages schedules)

**Would you like me to proceed with implementing:**

1. The Spark Structured Streaming application for Kafka → HDFS with LSTM predictions?
2. The Airflow DAG for pattern analysis?
3. Both?
