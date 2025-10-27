## ML Training Using PySpark

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
docker rm -f jupyter-spark 2>/dev/null

# Start a new Jupyter PySpark container
docker run -d --network custom_network -p 8888:8888 --name jupyter-spark jupyter/pyspark-notebook

# Get the Jupyter server token
docker exec jupyter-spark jupyter notebook list

docker exec jupyter-spark pip install hdfs
```

### 3. Access Jupyter Notebook
1. Copy the token from the output of the last command
2. Open in browser: http://localhost:8888
3. Enter the token when prompted

### 4. Access Web UIs (Remote Server Setup)
```bash
# Port forward all necessary services to local machine
ssh -L 8888:localhost:8888 \
    -L 8080:localhost:8080 \
    -L 9870:localhost:9870 \
    -L 8090:localhost:8090 \
    -L 4040:localhost:4040 \
    -L 4041:localhost:4041 \
    username@remote-server

# Or if using VS Code Remote SSH, configure port forwarding in .ssh/config:
# Host remote-server
#   HostName your-server-address
#   User your-username
#   LocalForward 8888 localhost:8888
#   LocalForward 8080 localhost:8080
#   LocalForward 9870 localhost:9870
#   LocalForward 8090 localhost:8090
#   LocalForward 4040 localhost:4040
#   LocalForward 4041 localhost:4041
```

Then access the services at:
- Jupyter Notebook: http://localhost:8888
- Spark Master UI: http://localhost:8080
- Spark Application UI: http://localhost:4040 or http://localhost:4041 (dynamic port)
- HDFS UI: http://localhost:9870
- Airflow UI: http://localhost:8090

### 5. Stop Services
```bash
# When done, stop all services
cd BigDataCluster
make stop-all

# Stop Jupyter container
docker rm -f jupyter-spark
```

