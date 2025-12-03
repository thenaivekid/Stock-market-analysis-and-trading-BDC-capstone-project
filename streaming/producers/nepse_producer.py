#!/usr/bin/env python3
"""
Real-Time NEPSE Stock Price Streamer with Kafka → HDFS
Streams live NEPSE stock prices to a single Kafka topic
"""

import sys
import os

# Add project root to sys.path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)


import json
import time
import signal
from datetime import datetime

try:
    from kafka import KafkaProducer
except ImportError:
    print("❌ kafka-python not installed! Run: pip install kafka-python")
    sys.exit(1)

# Try to import the scraper service
try:
    from scraper.app.services.market_data import MarketDataService

except ImportError:
    print("❌ Could not import MarketDataService. Make sure scraper/app is in path.")
    sys.exit(1)

# Configuration
KAFKA_BROKER = os.getenv('KAFKA_BROKER', 'localhost:9092')  # container hostname
TOPIC = os.getenv('KAFKA_TOPIC', 'nepse-stream')        # single topic for HDFS sink

running = True
def signal_handler(sig, frame):
    global running
    print("\n🛑 Shutting down streamer...")
    running = False
signal.signal(signal.SIGINT, signal_handler)


class NEPSEStreamer:
    """Real-time NEPSE stock streamer for Kafka → HDFS"""

    def __init__(self, broker: str = KAFKA_BROKER, topic: str = TOPIC):
        self.broker = broker
        self.topic = topic
        self.market_service = MarketDataService()
        self.producer = None
        self.stats = {
            'messages_sent': 0,
            'errors': 0,
            'start_time': time.time()
        }

    def connect(self):
        """Connect to Kafka"""
        print(f"📡 Connecting to Kafka broker: {self.broker}")
        try:
            self.producer = KafkaProducer(
                bootstrap_servers=[self.broker],
                value_serializer=lambda v: json.dumps(v).encode('utf-8'),
                compression_type='gzip',
                max_in_flight_requests_per_connection=5,
                retries=3
            )
            print("✅ Connected to Kafka!")
            return True
        except Exception as e:
            print(f"❌ Failed to connect to Kafka: {e}")
            return False

    def send_to_kafka(self, data: dict):
        """Send single stock record to Kafka"""
        try:
            # Add timestamp for streaming
            data['stream_timestamp'] = datetime.utcnow().isoformat()
            future = self.producer.send(self.topic, data)
            future.get(timeout=1)
            self.stats['messages_sent'] += 1
            return True
        except Exception as e:
            self.stats['errors'] += 1
            print(f"❌ Kafka send error: {e}")
            return False

    def fetch_and_stream(self):
        """Fetch live stock data and stream to Kafka"""
        try:
            stocks = self.market_service.fetch_live_data()
            for stock in stocks:
                if not running:
                    break
                self.send_to_kafka(stock)
            return len(stocks)
        except Exception as e:
            self.stats['errors'] += 1
            print(f"⚠️  Fetch error: {e}")
            return 0

    def run(self, interval_ms: int = 100):                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             
        """Main loop"""
        if not self.connect():
            return

        print(f"⚡ Streaming NEPSE data to Kafka topic: {self.topic}")
        iteration = 0
        while running:
            iteration += 1
            start = time.time()

            count = self.fetch_and_stream()

            # Print stats every 10 iterations
            if iteration % 10 == 0:
                uptime = time.time() - self.stats['start_time']
                rate = self.stats['messages_sent'] / uptime if uptime > 0 else 0
                print(f"[{datetime.now().strftime('%H:%M:%S')}] "
                      f"Stocks: {count} | Sent: {self.stats['messages_sent']} | "
                      f"Rate: {rate:.1f} msg/s")

            # Maintain interval
            sleep_time = max(0, (interval_ms / 1000.0) - (time.time() - start))
            if sleep_time > 0:
                time.sleep(sleep_time)

        self.cleanup()

    def cleanup(self):
        """Flush and close producer"""
        print("📊 Final stats:")
        print(f"Messages sent: {self.stats['messages_sent']}")
        print(f"Errors: {self.stats['errors']}")
        if self.producer:
            self.producer.flush()
            self.producer.close()
            print("✅ Kafka producer closed.")


def main():
    interval = 100  # default 100ms
    if len(sys.argv) > 1:
        try:
            interval = int(sys.argv[1])
        except ValueError:
            print(f"Invalid interval, using default: {interval}ms")
    streamer = NEPSEStreamer()
    streamer.run(interval_ms=interval)


if __name__ == "__main__":
    main()
