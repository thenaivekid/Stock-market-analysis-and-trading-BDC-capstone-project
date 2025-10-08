#!/usr/bin/env python3
"""
Real-Time NEPSE Stock Price Streamer with Kafka
Fetches live stock prices every 100ms and streams to Kafka

This is a PRODUCTION-READY streaming application!
"""

import sys
import os
import json
import time
import signal
from datetime import datetime
from typing import Dict, List

# Add scraper services to path (works both locally and in container)
if os.path.exists('/tmp/services'):
    sys.path.insert(0, '/tmp')  # Running in container
elif os.path.exists('/workspaces/Stock-market-analysis-and-trading-BDC-capstone-project/scraper/app'):
    sys.path.insert(0, '/workspaces/Stock-market-analysis-and-trading-BDC-capstone-project/scraper/app')  # Running locally
else:
    # Try relative path
    script_dir = os.path.dirname(os.path.abspath(__file__))
    scraper_path = os.path.join(script_dir, '../../scraper/app')
    if os.path.exists(scraper_path):
        sys.path.insert(0, scraper_path)

try:
    from kafka import KafkaProducer, KafkaConsumer
    from kafka.errors import KafkaError
except ImportError:
    print("❌ kafka-python not installed!")
    print("Run: pip install kafka-python")
    sys.exit(1)

try:
    from services.market_data import MarketDataService
except ImportError:
    print("❌ Could not import MarketDataService")
    print("Make sure scraper/app is in the path")
    sys.exit(1)

# Configuration
# Use environment variable or default to localhost (for dev) / kafka (for container)
KAFKA_BROKER = os.getenv('KAFKA_BROKER', 'localhost:9092')
TOPIC_LIVE_PRICES = 'nepse-live-prices'
TOPIC_TOP_GAINERS = 'nepse-top-gainers'
TOPIC_TOP_LOSERS = 'nepse-top-losers'
TOPIC_MARKET_SUMMARY = 'nepse-market-summary'

running = True

def signal_handler(sig, frame):
    """Handle Ctrl+C gracefully"""
    global running
    print("\n\n🛑 Shutting down streamer...")
    running = False

signal.signal(signal.SIGINT, signal_handler)


class NEPSEStreamer:
    """Real-time NEPSE stock price streamer"""
    
    def __init__(self, broker: str = KAFKA_BROKER):
        """Initialize the streamer"""
        self.broker = broker
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
                compression_type='gzip',  # Compress data for efficiency
                max_in_flight_requests_per_connection=5,
                retries=3
            )
            print("✅ Connected to Kafka!")
            return True
        except Exception as e:
            print(f"❌ Failed to connect to Kafka: {e}")
            print("Make sure Kafka is running: docker ps | grep kafka")
            return False
    
    def send_to_kafka(self, topic: str, data: dict):
        """Send data to Kafka topic"""
        try:
            # Add timestamp
            data['stream_timestamp'] = datetime.now().isoformat()
            
            future = self.producer.send(topic, data)
            future.get(timeout=1)  # Wait for confirmation
            self.stats['messages_sent'] += 1
            return True
        except KafkaError as e:
            self.stats['errors'] += 1
            print(f"❌ Kafka error: {e}")
            return False
        except Exception as e:
            self.stats['errors'] += 1
            print(f"❌ Error sending to Kafka: {e}")
            return False
    
    def fetch_and_stream(self):
        """Fetch live data and stream to Kafka"""
        try:
            # Fetch all live stocks
            stocks = self.market_service.fetch_live_data()
            
            # Stream individual stock updates
            for stock in stocks:
                if not running:
                    break
                self.send_to_kafka(TOPIC_LIVE_PRICES, stock)
            
            # Get and stream top gainers
            try:
                gainers = self.market_service.get_top_gainers(10)
                self.send_to_kafka(TOPIC_TOP_GAINERS, {
                    'timestamp': datetime.now().isoformat(),
                    'gainers': gainers
                })
            except:
                pass
            
            # Get and stream top losers
            try:
                losers = self.market_service.get_top_losers(10)
                self.send_to_kafka(TOPIC_TOP_LOSERS, {
                    'timestamp': datetime.now().isoformat(),
                    'losers': losers
                })
            except:
                pass
            
            # Get and stream market summary
            try:
                summary = self.market_service.get_market_summary()
                self.send_to_kafka(TOPIC_MARKET_SUMMARY, summary)
            except:
                pass
            
            return len(stocks)
            
        except Exception as e:
            print(f"⚠️  Error fetching data: {e}")
            self.stats['errors'] += 1
            return 0
    
    def run(self, interval_ms: int = 100):
        """
        Run the streamer continuously
        
        Args:
            interval_ms: Interval between fetches in milliseconds (default: 100ms)
        """
        if not self.connect():
            return
        
        print("=" * 70)
        print("⚡ NEPSE REAL-TIME STOCK STREAMER")
        print("=" * 70)
        print(f"Streaming interval: {interval_ms}ms")
        print(f"Kafka topics:")
        print(f"  - {TOPIC_LIVE_PRICES} (all stocks)")
        print(f"  - {TOPIC_TOP_GAINERS} (top 10 gainers)")
        print(f"  - {TOPIC_TOP_LOSERS} (top 10 losers)")
        print(f"  - {TOPIC_MARKET_SUMMARY} (market stats)")
        print("")
        print("Press Ctrl+C to stop")
        print("=" * 70)
        print("")
        
        iteration = 0
        
        try:
            while running:
                iteration += 1
                start = time.time()
                
                # Fetch and stream data
                stock_count = self.fetch_and_stream()
                
                elapsed = (time.time() - start) * 1000  # Convert to ms
                
                # Calculate actual interval achieved
                actual_interval = (time.time() - start) * 1000
                
                # Print status every 10 iterations
                if iteration % 10 == 0:
                    uptime = time.time() - self.stats['start_time']
                    rate = self.stats['messages_sent'] / uptime if uptime > 0 else 0
                    
                    # Show if we're meeting target interval
                    status_icon = "✅" if actual_interval <= interval_ms else "⚠️"
                    
                    print(f"{status_icon} [{datetime.now().strftime('%H:%M:%S.%f')[:-3]}] "
                          f"Stocks: {stock_count} | "
                          f"Sent: {self.stats['messages_sent']} msgs | "
                          f"Rate: {rate:.1f} msg/s | "
                          f"Fetch: {elapsed:.0f}ms | "
                          f"Target: {interval_ms}ms | "
                          f"Actual: {actual_interval:.0f}ms")
                
                # Sleep for remaining time to maintain interval
                sleep_time = max(0, (interval_ms / 1000.0) - (time.time() - start))
                if sleep_time > 0:
                    time.sleep(sleep_time)
                elif iteration % 10 == 0:
                    print(f"   ⚠️  WARNING: Fetch time ({elapsed:.0f}ms) exceeds target interval ({interval_ms}ms)!")
        
        finally:
            self.cleanup()
    
    def cleanup(self):
        """Cleanup resources"""
        print("\n" + "=" * 70)
        print("📊 FINAL STATISTICS")
        print("=" * 70)
        
        uptime = time.time() - self.stats['start_time']
        rate = self.stats['messages_sent'] / uptime if uptime > 0 else 0
        
        print(f"Messages sent: {self.stats['messages_sent']}")
        print(f"Errors: {self.stats['errors']}")
        print(f"Uptime: {uptime:.1f} seconds")
        print(f"Average rate: {rate:.1f} messages/second")
        print("=" * 70)
        
        if self.producer:
            print("Flushing Kafka producer...")
            self.producer.flush()
            self.producer.close()
            print("✅ Kafka connection closed")


def main():
    """Main entry point"""
    print("\n🚀 Starting NEPSE Real-Time Stock Streamer...")
    print("")
    
    # Get interval from command line or use default
    interval = 100  # Default 100ms
    if len(sys.argv) > 1:
        try:
            interval = int(sys.argv[1])
            print(f"Using custom interval: {interval}ms")
        except ValueError:
            print(f"Invalid interval, using default: {interval}ms")
    
    streamer = NEPSEStreamer(broker=KAFKA_BROKER)
    streamer.run(interval_ms=interval)


if __name__ == "__main__":
    main()
