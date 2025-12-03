#!/usr/bin/env python3
"""
NEPSE Kafka -> HDFS Sink
Consumes live stock market data from Kafka and writes to HDFS in CSV format.

Features:
- Parses all rows from table format messages
- Buffers messages (500 messages or 5 seconds, whichever comes first)
- Appends directly to HDFS CSV
- Adds header only if file doesn't exist
"""

import os
import sys
import re
import time
import signal
import csv
from datetime import datetime
from threading import Lock

try:
    from kafka import KafkaConsumer
    from kafka.errors import KafkaError
except ImportError:
    print("❌ kafka-python not installed! Run: pip install kafka-python")
    sys.exit(1)

try:
    from hdfs import InsecureClient, HdfsError
except ImportError:
    print("❌ hdfs library not installed! Run: pip install hdfs")
    sys.exit(1)

# ---------------- Configuration ----------------
KAFKA_BROKER = os.getenv('KAFKA_BROKER', 'localhost:9092')
KAFKA_TOPIC = os.getenv('KAFKA_TOPIC', 'nepse-stream')
HDFS_URL = os.getenv('HDFS_URL', 'http://localhost:9870')  # use container name if inside Docker
HDFS_USER = os.getenv('HDFS_USER', 'hdfs')
HDFS_PATH = os.getenv('HDFS_PATH', '/user/hdfs/nepse_dashboard.csv')

BATCH_SIZE = int(os.getenv('BATCH_SIZE', '500'))
BATCH_TIMEOUT = int(os.getenv('BATCH_TIMEOUT', '5'))  # seconds

running = True

# ---------------- Signal Handling ----------------
def signal_handler(sig, frame):
    global running
    print("\n🛑 Shutting down HDFS sink...")
    running = False

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

# ---------------- Table Parsing ----------------
def parse_table(message: str):
    """
    Parse all rows in the NEPSE table message
    Returns a list of dicts
    """
    rows = []
    for line in message.splitlines():
        match = re.match(r"│\s*(\S+)\s*│\s*([\d,.]+)\s*│\s*([+\-\d.]+)%?\s*│\s*([\d,]+)\s*│", line)
        if match:
            symbol, last_price, change, volume = match.groups()
            # Skip header rows
            if symbol.lower() in ['symbol', 'stock']:
                continue
            rows.append({
                "symbol": symbol,
                "last_price": last_price.replace(',', ''),
                "percent_change": change.replace('+', '').replace('%', ''),
                "volume": volume.replace(',', ''),
                "timestamp": datetime.utcnow().isoformat()
            })
    return rows

# ---------------- NEPSE HDFS Sink ----------------
class NEPSEHDFSSink:
    def __init__(self):
        self.consumer = None
        self.hdfs_client = None
        self.buffer = []
        self.buffer_lock = Lock()
        self.last_write_time = time.time()
        self.file_exists = False

    def connect_kafka(self):
        print(f"📡 Connecting to Kafka: {KAFKA_BROKER}")
        try:
            self.consumer = KafkaConsumer(
                KAFKA_TOPIC,
                bootstrap_servers=[KAFKA_BROKER],
                value_deserializer=lambda m: m.decode('utf-8'),
                auto_offset_reset='latest',
                enable_auto_commit=True,
                group_id='nepse-hdfs-sink'
            )
            print("✅ Connected to Kafka!")
        except Exception as e:
            print(f"❌ Kafka connection error: {e}")
            sys.exit(1)

    def connect_hdfs(self):
        print(f"📡 Connecting to HDFS: {HDFS_URL} (user={HDFS_USER})")
        try:
            self.hdfs_client = InsecureClient(HDFS_URL, user=HDFS_USER)
            dir_path = os.path.dirname(HDFS_PATH)
            self.hdfs_client.makedirs(dir_path)
            # Check if file exists
            try:
                self.hdfs_client.status(HDFS_PATH)
                self.file_exists = True
                print(f"📄 HDFS file exists: {HDFS_PATH}")
            except HdfsError:
                self.file_exists = False
                print(f"📄 HDFS file will be created: {HDFS_PATH}")
        except Exception as e:
            print(f"❌ HDFS connection error: {e}")
            sys.exit(1)

    def add_to_buffer(self, records):
        with self.buffer_lock:
            self.buffer.extend(records)

    def should_flush(self):
        with self.buffer_lock:
            buffer_size = len(self.buffer)
        return buffer_size >= BATCH_SIZE or (time.time() - self.last_write_time) >= BATCH_TIMEOUT

    def flush_buffer(self):
        with self.buffer_lock:
            if not self.buffer:
                return
            records_to_write = self.buffer.copy()
            self.buffer.clear()

        if not records_to_write:
            return

        try:
            # Prepare CSV content
            output_lines = []
            if not self.file_exists:
                header = "symbol,last_price,percent_change,volume,timestamp\n"
                output_lines.append(header)
                self.file_exists = True

            for record in records_to_write:
                line = f"{record['symbol']},{record['last_price']},{record['percent_change']},{record['volume']},{record['timestamp']}\n"
                output_lines.append(line)

            # Append to HDFS
            with self.hdfs_client.write(HDFS_PATH, encoding='utf-8', append=True) as f:
                f.writelines(output_lines)

            self.last_write_time = time.time()
            print(f"✅ Flushed {len(records_to_write)} records to HDFS")
        except Exception as e:
            print(f"❌ Failed to flush buffer to HDFS: {e}")
            # Re-add records to buffer
            with self.buffer_lock:
                self.buffer = records_to_write + self.buffer

    def process_message(self, message_value: str):
        records = parse_table(message_value)
        if records:
            self.add_to_buffer(records)

    def run(self):
        self.connect_kafka()
        self.connect_hdfs()
        print("⚡ Starting HDFS sink...")
        try:
            while running:
                for msg in self.consumer:
                    if not running:
                        break
                    self.process_message(msg.value)

                    if self.should_flush():
                        self.flush_buffer()
                time.sleep(0.1)
        finally:
            print("\n📊 Flushing remaining buffer...")
            self.flush_buffer()
            if self.consumer:
                self.consumer.close()
                print("✅ Kafka consumer closed")
            print("✅ HDFS sink stopped")

# ---------------- Main ----------------
if __name__ == "__main__":
    sink = NEPSEHDFSSink()
    sink.run()
