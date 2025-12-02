#!/usr/bin/env python3
"""
Real-Time NEPSE Stock Price Dashboard
Consumes from Kafka and displays live data in terminal.
"""

import sys
import os
import json
import signal
from datetime import datetime
from collections import defaultdict

try:
    from kafka import KafkaConsumer
except ImportError:
    print("❌ kafka-python not installed! Run: pip install kafka-python")
    sys.exit(1)

# ---------------------------
# Configuration
# ---------------------------
KAFKA_BROKER = os.getenv('KAFKA_BROKER', 'localhost:9092')
TOPICS = ['nepse-live-prices', 'nepse-top-gainers', 'nepse-top-losers', 'nepse-market-summary']

running = True

# ---------------------------
# Signal handling
# ---------------------------
def signal_handler(sig, frame):
    global running
    print("\n🛑 Shutting down dashboard...")
    running = False

signal.signal(signal.SIGINT, signal_handler)

# ---------------------------
# Dashboard class
# ---------------------------
class LiveDashboard:
    """Real-time NEPSE dashboard consuming Kafka topics"""

    def __init__(self, broker: str = KAFKA_BROKER):
        self.broker = broker
        self.consumer = None
        self.stats = {
            'messages_received': 0,
            'by_topic': defaultdict(int)
        }
        self.latest_data = {
            'stocks': {},
            'gainers': [],
            'losers': [],
            'summary': {}
        }

    def connect(self):
        """Connect to Kafka broker"""
        print(f"📡 Connecting to Kafka broker: {self.broker}")
        try:
            self.consumer = KafkaConsumer(
                *TOPICS,
                bootstrap_servers=[self.broker],
                value_deserializer=lambda m: json.loads(m.decode('utf-8')),
                auto_offset_reset='latest',
                enable_auto_commit=True,
                group_id='nepse-dashboard'
            )
            print("✅ Connected to Kafka!")
            print(f"📋 Subscribed to topics: {', '.join(TOPICS)}")
            return True
        except Exception as e:
            print(f"❌ Failed to connect to Kafka: {e}")
            return False

    # ---------------------------
    # Display helpers
    # ---------------------------
    def format_price(self, price):
        try:
            return f"Rs. {float(price):,.2f}"
        except:
            return "N/A"

    def format_change(self, change):
        try:
            change_val = float(change)
            if change_val > 0:
                return f"🟢 +{change_val:.2f}%"
            elif change_val < 0:
                return f"🔴 {change_val:.2f}%"
            return f"⚪ {change_val:.2f}%"
        except:
            return "N/A"

    def display_stock_update(self, stock):
        symbol = stock.get('symbol', 'N/A')
        ltp = self.format_price(stock.get('lastTradedPrice'))
        change = self.format_change(stock.get('percentageChange'))
        volume = stock.get('totalTradeQuantity', 0)
        print(f"  📈 {symbol:8s} | {ltp:15s} | {change:15s} | Vol: {volume:,}")

    def display_summary(self, summary):
        print("\n" + "=" * 70)
        print("📊 MARKET SUMMARY")
        print("=" * 70)
        print(f"Total Stocks:     {summary.get('totalStocks', 'N/A')}")
        print(f"🟢 Advancing:     {summary.get('advancing', 'N/A')}")
        print(f"🔴 Declining:     {summary.get('declining', 'N/A')}")
        print(f"⚪ Unchanged:     {summary.get('unchanged', 'N/A')}")
        print(f"Total Turnover:   Rs. {summary.get('totalTurnover', 0):,.2f}")
        print(f"Total Volume:     {summary.get('totalVolume', 0):,}")
        print(f"Total Trades:     {summary.get('totalTransactions', 0):,}")

    def display_top_stocks(self, stocks, title="Top Stocks", count=5):
        print(f"\n{title}")
        print("-" * 50)
        for i, stock in enumerate(stocks[:count], 1):
            symbol = stock.get('symbol', 'N/A')
            change = self.format_change(stock.get('percentageChange'))
            ltp = self.format_price(stock.get('lastTradedPrice'))
            print(f"{i:2d}. {symbol:8s} | {ltp:15s} | {change}")

    # ---------------------------
    # Main consumer loop
    # ---------------------------
    def run(self, mode: str = 'compact'):
        if not self.connect():
            return

        print("\n⚡ NEPSE LIVE STOCK DASHBOARD")
        print("=" * 70)
        print(f"Mode: {mode}")
        print("Waiting for live data from Kafka...")
        print("Press Ctrl+C to stop")
        print("=" * 70)

        last_summary_display = 0
        summary_interval = 5  # seconds

        try:
            for message in self.consumer:
                if not running:
                    break

                topic = message.topic
                data = message.value

                self.stats['messages_received'] += 1
                self.stats['by_topic'][topic] += 1

                if topic == 'nepse-live-prices':
                    symbol = data.get('symbol')
                    if symbol:
                        self.latest_data['stocks'][symbol] = data
                    if mode == 'verbose':
                        self.display_stock_update(data)

                elif topic == 'nepse-top-gainers':
                    self.latest_data['gainers'] = data.get('gainers', [])
                    if mode == 'verbose':
                        self.display_top_stocks(self.latest_data['gainers'], title="🟢 TOP GAINERS")

                elif topic == 'nepse-top-losers':
                    self.latest_data['losers'] = data.get('losers', [])
                    if mode == 'verbose':
                        self.display_top_stocks(self.latest_data['losers'], title="🔴 TOP LOSERS")

                elif topic == 'nepse-market-summary':
                    self.latest_data['summary'] = data
                    current_time = datetime.now().timestamp()
                    if mode == 'compact' and (current_time - last_summary_display) >= summary_interval:
                        print(f"\n⏰ {datetime.now().strftime('%H:%M:%S')} - Live Update")
                        self.display_summary(data)
                        if self.latest_data['gainers']:
                            self.display_top_stocks(self.latest_data['gainers'], title="🟢 Top 5 Gainers")
                        if self.latest_data['losers']:
                            self.display_top_stocks(self.latest_data['losers'], title="🔴 Top 5 Losers")
                        last_summary_display = current_time

        finally:
            self.cleanup()

    def cleanup(self):
        print("\n📊 SESSION STATISTICS")
        print("=" * 70)
        print(f"Total messages: {self.stats['messages_received']}")
        print("\nBy topic:")
        for topic, count in self.stats['by_topic'].items():
            print(f"  {topic}: {count}")
        if self.consumer:
            self.consumer.close()
            print("✅ Kafka connection closed")

# ---------------------------
# Main entry
# ---------------------------
def main():
    print("\n🚀 Starting NEPSE Live Dashboard...")
    mode = 'compact'
    if len(sys.argv) > 1 and sys.argv[1] in ['compact', 'verbose']:
        mode = sys.argv[1]

    dashboard = LiveDashboard(broker=KAFKA_BROKER)
    dashboard.run(mode=mode)

if __name__ == "__main__":
    main()
