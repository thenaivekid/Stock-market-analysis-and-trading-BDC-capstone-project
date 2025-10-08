# Big Data Cluster with Spark, HDFS, Kafka and Airflow
## How to run the task
The project is dockerized, to start all services run: 

```bash
make start-all
```

This process will start four docker-compose clusters, all sharing the same network:
1. **Airflow**: It will run a standalone airflow. You can access it from: http://localhost:8090. You can log in with user=admin and password=admin
2. **HDFS**: It will run the HDFS cluster. You can access the namenode UI from: http://localhost:9870
3. **Spark**: It will run the spark cluster. You can access the spark UI from: http://localhost:8080
4. **Kafka**: It will run the kafka cluster. You can send events to kafka at: kafka:9092

Once all services are up and running, you should configure the Spark Connection in Airflow. To do so, go to Admin -> 
Connections -> spark_default and fill the form with the following values:
+ Conn Id: spark_default
+ Conn Type: Spark
+ Host: spark://spark-spark-1
+ Port: 7077
+ Extra: {"deploy-mode": "client"}

Then you can run the etl_task DAG on Airflow UI.

To stop all services run:

```bash
make stop-all
```

## Tests
To test the spark etl, run:

```bash
make test
``` 

## Important notes
+ The project is intended to work with an arm64 architecture, although modifying Airflow Dockerfile as follows should do the trick for amd64:
```bash
ENV JAVA_HOME /usr/lib/jvm/java-11-openjdk-amd64
```

