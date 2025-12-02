#!/usr/bin/env python3
"""
NEPSE Kafka to HDFS Sink
Consumes live stock market data from Kafka topic 'nepse-stream' and writes to HDFS in CSV format.

Features:
- Parses text table format messages from Kafka
- Buffers messages (500 messages or 5 seconds, whichever comes first)
- Writes to HDFS at '/user/hdfs/nepse_dashboard.csv'
- Handles connection errors gracefully
- Runs indefinitely until interrupted
"""

import os
import sys
import re
import time
import signal
import csv
import io
from datetime import datetime
from typing import List, Dict, Optional
from threading import Lock

try:
    from kafka import KafkaConsumer
    from kafka.errors import KafkaError
except ImportError:
    print("❌ kafka-python not installed! Run: pip install kafka-python")
    sys.exit(1)

try:
    import requests
except ImportError:
    print("❌ requests library not installed! Run: pip install requests")
    sys.exit(1)

# Configuration
KAFKA_BROKER = os.getenv('KAFKA_BROKER', 'localhost:9092')
KAFKA_TOPIC = os.getenv('KAFKA_TOPIC', 'nepse-stream')
HDFS_URL = os.getenv('HDFS_URL', 'http://localhost:9870')
HDFS_USER = os.getenv('HDFS_USER', 'hdfs')
HDFS_PATH = os.getenv('HDFS_PATH', '/user/hdfs/nepse_dashboard.csv')

# Batching configuration
BATCH_SIZE = int(os.getenv('BATCH_SIZE', '500'))  # Write every 500 messages
BATCH_TIMEOUT = int(os.getenv('BATCH_TIMEOUT', '5'))  # Or every 5 seconds

running = True


def signal_handler(sig, frame):
    """Handle Ctrl+C gracefully"""
    global running
    print("\n🛑 Shutting down HDFS sink...")
    running = False


signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)


class TableParser:
    """Parser for text table format messages"""
    
    @staticmethod
    def parse_table_message(message: str) -> Optional[Dict[str, str]]:
        """
        Parse a text table format message like:
        │ Symbol   │ Last Price │ % Change │ Volume │
        │ JHAPA    │ 976.00     │ +10.00%  │ 1,260  │
        
        Returns a dict with keys: symbol, last_price, percent_change, volume
        """
        try:
            lines = [line.strip() for line in message.strip().split('\n') if line.strip()]
            if len(lines) < 2:
                return None
            
            # Find data rows (lines that start with │)
            data_lines = [line for line in lines if line.startswith('│')]
            
            if len(data_lines) < 2:
                return None
            
            # Skip the first line (header) and parse the first data row
            # Header typically contains "Symbol", "Last Price", etc.
            header_line = data_lines[0].lower()
            if 'symbol' in header_line and 'price' in header_line:
                # First line is header, use second line as data
                data_line = data_lines[1] if len(data_lines) > 1 else None
            else:
                # No clear header, use first data line
                data_line = data_lines[0]
            
            if not data_line:
                return None
            
            # Split by │ and clean up
            parts = [p.strip() for p in data_line.split('│') if p.strip()]
            
            if len(parts) < 4:
                # Try alternative parsing - handle different table formats
                # Remove │ characters and split by whitespace
                cleaned = re.sub(r'[│┃]', ' ', data_line)
                parts = [p.strip() for p in cleaned.split() if p.strip()]
            
            if len(parts) >= 4:
                symbol = parts[0].strip()
                last_price = parts[1].strip().replace(',', '')
                percent_change = parts[2].strip().replace('%', '').replace('+', '').replace(',', '')
                volume = parts[3].strip().replace(',', '')
                
                # Skip if this looks like a header row
                if symbol.lower() in ['symbol', 'stock'] or 'price' in symbol.lower():
                    return None
                
                return {
                    'symbol': symbol,
                    'last_price': last_price,
                    'percent_change': percent_change,
                    'volume': volume,
                    'timestamp': datetime.utcnow().isoformat()
                }
            
            return None
            
        except Exception as e:
            print(f"⚠️  Error parsing message: {e}")
            print(f"   Message: {message[:100]}...")
            return None


class WebHDFSClient:
    """Simple WebHDFS client using REST API"""
    
    def __init__(self, namenode_url: str, user: str = 'hdfs'):
        self.namenode_url = namenode_url.rstrip('/')
        self.user = user
        self.webhdfs_url = f"{self.namenode_url}/webhdfs/v1"
        # Extract hostname and port from namenode URL for redirect replacement
        from urllib.parse import urlparse
        parsed = urlparse(self.namenode_url)
        self.namenode_host = parsed.hostname or 'localhost'
        self.namenode_port = parsed.port or (9870 if '9870' in self.namenode_url else 50070)
    
    def _fix_redirect_url(self, redirect_url: str) -> str:
        """Fix redirect URL by replacing Docker container hostnames with localhost"""
        from urllib.parse import urlparse, urlunparse
        import re
        parsed = urlparse(redirect_url)
        
        # Replace any Docker container hostname (usually hex strings or container names) with localhost
        hostname = parsed.hostname
        if hostname and hostname != 'localhost' and hostname != '127.0.0.1':
            # Check if it looks like a Docker container hostname
            # (hex strings like c811b5238351, container names, etc.)
            # Keep IP addresses and proper domain names
            is_ip = re.match(r'^\d+\.\d+\.\d+\.\d+$', hostname)
            is_domain = '.' in hostname and not re.match(r'^[a-f0-9]{12}$', hostname)  # Not a hex container ID
            
            if not (is_ip or is_domain):
                # This looks like a Docker container hostname - replace with localhost
                # But keep the port - we'll try localhost first
                new_netloc = f"localhost:{parsed.port}" if parsed.port else "localhost"
                fixed = urlunparse((
                    parsed.scheme,
                    new_netloc,
                    parsed.path,
                    parsed.params,
                    parsed.query,
                    parsed.fragment
                ))
                return fixed
        
        return redirect_url
    
    def _make_request(self, method: str, path: str, params: dict = None, data: bytes = None, 
                      allow_redirects: bool = False) -> requests.Response:
        """Make a WebHDFS REST API request"""
        url = f"{self.webhdfs_url}{path}"
        if params is None:
            params = {}
        params['user.name'] = self.user
        
        if method.upper() == 'PUT' and data:
            # For PUT requests, first get redirect URL
            response = requests.put(url, params=params, allow_redirects=False, timeout=30)
            if response.status_code in [307, 308]:  # Temporary/ Permanent redirect
                redirect_url = response.headers.get('Location')
                if redirect_url:
                    # Fix the redirect URL to use localhost instead of container hostname
                    fixed_url = self._fix_redirect_url(redirect_url)
                    try:
                        return requests.put(fixed_url, data=data, timeout=30)
                    except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e:
                        # If localhost doesn't work, the datanode port might not be exposed
                        # Provide helpful error message
                        from urllib.parse import urlparse
                        parsed_redirect = urlparse(redirect_url)
                        if parsed_redirect.port == 9864:
                            print(f"⚠️  Warning: Datanode WebHDFS port 9864 not accessible. "
                                  f"Make sure it's exposed in docker-compose.yml")
                        # Try original redirect as fallback (might work if running inside Docker)
                        try:
                            return requests.put(redirect_url, data=data, timeout=30)
                        except Exception:
                            raise e
            return response
        elif method.upper() == 'POST' and data:
            response = requests.post(url, params=params, allow_redirects=False, timeout=30)
            if response.status_code in [307, 308]:
                redirect_url = response.headers.get('Location')
                if redirect_url:
                    fixed_url = self._fix_redirect_url(redirect_url)
                    try:
                        return requests.post(fixed_url, data=data, timeout=30)
                    except requests.exceptions.ConnectionError:
                        return requests.post(redirect_url, data=data, timeout=30)
            return response
        else:
            return requests.request(method, url, params=params, allow_redirects=allow_redirects, timeout=30)
    
    def makedirs(self, path: str):
        """Create directory (and parents) if it doesn't exist"""
        try:
            params = {'op': 'MKDIRS'}
            response = self._make_request('PUT', path, params=params)
            response.raise_for_status()
        except requests.exceptions.RequestException:
            pass  # Directory might already exist
    
    def exists(self, path: str) -> bool:
        """Check if file/directory exists"""
        try:
            params = {'op': 'GETFILESTATUS'}
            response = self._make_request('GET', path, params=params)
            return response.status_code == 200
        except requests.exceptions.RequestException:
            return False
    
    def read(self, path: str) -> bytes:
        """Read file from HDFS"""
        params = {'op': 'OPEN'}
        response = self._make_request('GET', path, params=params, allow_redirects=True)
        response.raise_for_status()
        return response.content
    
    def write(self, path: str, data: bytes, overwrite: bool = True):
        """Write data to HDFS file"""
        params = {'op': 'CREATE', 'overwrite': str(overwrite).lower()}
        response = self._make_request('PUT', path, params=params, data=data)
        response.raise_for_status()
        return response


class NEPSEHDFSSink:
    """Kafka consumer that writes to HDFS"""
    
    def __init__(self, 
                 kafka_broker: str = KAFKA_BROKER,
                 kafka_topic: str = KAFKA_TOPIC,
                 hdfs_url: str = HDFS_URL,
                 hdfs_user: str = HDFS_USER,
                 hdfs_path: str = HDFS_PATH):
        self.kafka_broker = kafka_broker
        self.kafka_topic = kafka_topic
        self.hdfs_url = hdfs_url
        self.hdfs_user = hdfs_user
        self.hdfs_path = hdfs_path
        
        self.consumer: Optional[KafkaConsumer] = None
        self.hdfs_client: Optional[WebHDFSClient] = None
        
        # Buffer for batching
        self.buffer: List[Dict[str, str]] = []
        self.buffer_lock = Lock()
        self.last_write_time = time.time()
        self.file_exists = False
        
        # Statistics
        self.stats = {
            'messages_consumed': 0,
            'messages_parsed': 0,
            'messages_written': 0,
            'batches_written': 0,
            'errors': 0,
            'start_time': time.time()
        }
    
    def connect_kafka(self) -> bool:
        """Connect to Kafka broker"""
        print(f"📡 Connecting to Kafka broker: {self.kafka_broker}")
        print(f"📋 Subscribing to topic: {self.kafka_topic}")
        
        try:
            self.consumer = KafkaConsumer(
                self.kafka_topic,
                bootstrap_servers=[self.kafka_broker],
                value_deserializer=lambda m: m.decode('utf-8'),  # Raw text, not JSON
                auto_offset_reset='latest',  # Start from latest messages
                enable_auto_commit=True,
                group_id='nepse-hdfs-sink',
                consumer_timeout_ms=1000  # Timeout for polling
            )
            print("✅ Connected to Kafka!")
            return True
        except Exception as e:
            print(f"❌ Failed to connect to Kafka: {e}")
            self.stats['errors'] += 1
            return False
    
    def connect_hdfs(self) -> bool:
        """Connect to HDFS"""
        print(f"📡 Connecting to HDFS: {self.hdfs_url} (user: {self.hdfs_user})")
        
        try:
            self.hdfs_client = WebHDFSClient(self.hdfs_url, user=self.hdfs_user)
            
            # Test connection by checking if namenode is accessible
            try:
                test_response = requests.get(f"{self.hdfs_url}/webhdfs/v1/?op=LISTSTATUS&user.name={self.hdfs_user}")
                if test_response.status_code in [200, 400, 404]:  # 400/404 means endpoint exists
                    print("✅ Connected to HDFS!")
                else:
                    print(f"⚠️  HDFS connection test returned status {test_response.status_code}")
            except Exception as e:
                print(f"⚠️  HDFS connection test failed: {e}")
                # Still try to continue, might be a permission issue
            
            # Check if file exists and create directory if needed
            dir_path = os.path.dirname(self.hdfs_path)
            try:
                self.hdfs_client.makedirs(dir_path)
                print(f"✅ Ensured HDFS directory exists: {dir_path}")
            except Exception:
                pass  # Directory might already exist
            
            # Check if file exists
            try:
                if self.hdfs_client.exists(self.hdfs_path):
                    self.file_exists = True
                    print(f"📄 HDFS file exists: {self.hdfs_path}")
                else:
                    self.file_exists = False
                    print(f"📄 HDFS file will be created: {self.hdfs_path}")
            except Exception:
                self.file_exists = False
                print(f"📄 HDFS file will be created: {self.hdfs_path}")
            
            return True
        except Exception as e:
            print(f"❌ Failed to connect to HDFS: {e}")
            self.stats['errors'] += 1
            return False
    
    def add_to_buffer(self, record: Dict[str, str]):
        """Add a parsed record to the buffer"""
        with self.buffer_lock:
            self.buffer.append(record)
    
    def flush_buffer(self) -> bool:
        """Write buffered records to HDFS"""
        with self.buffer_lock:
            if not self.buffer:
                return True
            
            records_to_write = self.buffer.copy()
            self.buffer.clear()
        
        if not records_to_write:
            return True
        
        try:
            # Create CSV content for new records only
            output = io.StringIO()
            writer = csv.DictWriter(
                output,
                fieldnames=['symbol', 'last_price', 'percent_change', 'volume', 'timestamp']
            )
            
            # Write records (no header, we'll handle that separately)
            for record in records_to_write:
                writer.writerow(record)
            
            new_csv_content = output.getvalue()
            
            # Append to HDFS file
            if self.hdfs_client:
                try:
                    # Check if file exists and read existing content
                    existing_content = ""
                    file_exists_now = False
                    
                    try:
                        if self.hdfs_client.exists(self.hdfs_path):
                            file_exists_now = True
                            # Read existing content
                            existing_bytes = self.hdfs_client.read(self.hdfs_path)
                            existing_content = existing_bytes.decode('utf-8')
                    except Exception:
                        # File doesn't exist, we'll create it with header
                        file_exists_now = False
                    
                    # Prepare final content
                    if not file_exists_now and not self.file_exists:
                        # First write - include header
                        output_with_header = io.StringIO()
                        writer_with_header = csv.DictWriter(
                            output_with_header,
                            fieldnames=['symbol', 'last_price', 'percent_change', 'volume', 'timestamp']
                        )
                        writer_with_header.writeheader()
                        header_content = output_with_header.getvalue()
                        final_content = header_content + new_csv_content
                        self.file_exists = True
                    else:
                        # Append to existing file
                        final_content = existing_content + new_csv_content
                    
                    # Write the content
                    self.hdfs_client.write(self.hdfs_path, final_content.encode('utf-8'), overwrite=True)
                    
                    self.stats['messages_written'] += len(records_to_write)
                    self.stats['batches_written'] += 1
                    self.last_write_time = time.time()
                    
                    print(f"✅ Wrote {len(records_to_write)} records to HDFS "
                          f"(Total: {self.stats['messages_written']} messages, "
                          f"{self.stats['batches_written']} batches)")
                    return True
                    
                except Exception as e:
                    print(f"❌ Failed to write to HDFS: {e}")
                    # Put records back in buffer to retry
                    with self.buffer_lock:
                        self.buffer = records_to_write + self.buffer
                    self.stats['errors'] += 1
                    return False
            
        except Exception as e:
            print(f"❌ Error preparing CSV content: {e}")
            # Put records back in buffer
            with self.buffer_lock:
                self.buffer = records_to_write + self.buffer
            self.stats['errors'] += 1
            return False
    
    def should_flush(self) -> bool:
        """Check if buffer should be flushed"""
        with self.buffer_lock:
            buffer_size = len(self.buffer)
        
        time_elapsed = time.time() - self.last_write_time
        
        return buffer_size >= BATCH_SIZE or time_elapsed >= BATCH_TIMEOUT
    
    def process_message(self, message_value: str):
        """Process a single Kafka message"""
        self.stats['messages_consumed'] += 1
        
        # Parse the message
        parsed = TableParser.parse_table_message(message_value)
        
        if parsed:
            self.stats['messages_parsed'] += 1
            self.add_to_buffer(parsed)
        else:
            # Try to handle JSON format as fallback
            try:
                import json
                data = json.loads(message_value)
                if isinstance(data, dict):
                    # Convert JSON format to our format
                    parsed = {
                        'symbol': data.get('symbol', ''),
                        'last_price': str(data.get('lastTradedPrice', data.get('last_price', ''))).replace(',', ''),
                        'percent_change': str(data.get('percentageChange', data.get('percent_change', ''))).replace('%', '').replace('+', ''),
                        'volume': str(data.get('totalTradeQuantity', data.get('volume', ''))).replace(',', ''),
                        'timestamp': data.get('stream_timestamp', datetime.utcnow().isoformat())
                    }
                    self.stats['messages_parsed'] += 1
                    self.add_to_buffer(parsed)
            except Exception:
                # Not JSON either, skip
                pass
    
    def run(self):
        """Main consumer loop"""
        if not self.connect_kafka():
            return
        
        if not self.connect_hdfs():
            return
        
        print(f"\n⚡ Starting HDFS sink consumer...")
        print(f"   Batch size: {BATCH_SIZE} messages")
        print(f"   Batch timeout: {BATCH_TIMEOUT} seconds")
        print(f"   HDFS path: {self.hdfs_path}")
        print(f"   Press Ctrl+C to stop\n")
        
        try:
            while running:
                try:
                    # Poll for messages
                    message_pack = self.consumer.poll(timeout_ms=1000)
                    
                    if message_pack:
                        for topic_partition, messages in message_pack.items():
                            for message in messages:
                                if not running:
                                    break
                                self.process_message(message.value)
                    
                    # Check if we should flush the buffer
                    if self.should_flush():
                        self.flush_buffer()
                    
                    # Print stats every 30 seconds
                    if int(time.time()) % 30 == 0:
                        uptime = time.time() - self.stats['start_time']
                        with self.buffer_lock:
                            buffer_size = len(self.buffer)
                        
                        print(f"[{datetime.now().strftime('%H:%M:%S')}] "
                              f"Consumed: {self.stats['messages_consumed']} | "
                              f"Parsed: {self.stats['messages_parsed']} | "
                              f"Written: {self.stats['messages_written']} | "
                              f"Batches: {self.stats['batches_written']} | "
                              f"Buffer: {buffer_size} | "
                              f"Errors: {self.stats['errors']} | "
                              f"Uptime: {int(uptime)}s")
                
                except KafkaError as e:
                    print(f"❌ Kafka error: {e}")
                    self.stats['errors'] += 1
                    # Try to reconnect
                    time.sleep(5)
                    if not self.connect_kafka():
                        break
                
                except Exception as e:
                    if not running:
                        break
                    print(f"❌ Unexpected error: {e}")
                    self.stats['errors'] += 1
                    time.sleep(1)
        
        finally:
            # Flush remaining buffer
            print("\n📊 Flushing remaining buffer...")
            self.flush_buffer()
            
            # Print final stats
            print("\n📊 Final Statistics:")
            print(f"   Messages consumed: {self.stats['messages_consumed']}")
            print(f"   Messages parsed: {self.stats['messages_parsed']}")
            print(f"   Messages written: {self.stats['messages_written']}")
            print(f"   Batches written: {self.stats['batches_written']}")
            print(f"   Errors: {self.stats['errors']}")
            uptime = time.time() - self.stats['start_time']
            print(f"   Uptime: {int(uptime)} seconds")
            
            # Close connections
            if self.consumer:
                self.consumer.close()
                print("✅ Kafka consumer closed")
            
            if self.hdfs_client:
                print("✅ HDFS connection closed")


def main():
    """Main entry point"""
    sink = NEPSEHDFSSink()
    sink.run()


if __name__ == "__main__":
    main()

