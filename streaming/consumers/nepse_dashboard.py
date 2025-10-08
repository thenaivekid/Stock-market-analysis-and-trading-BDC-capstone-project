#!/usr/bin/env python3
"""
Real-Time NEPSE Stock Price Dashboard
Consumes from Kafka and displays live data in terminal

This shows streaming data in real-time!
"""

import sys
import os
import json
import signal
from datetime import datetime
from collections import defaultdict

try:
    from kafka import KafkaConsumer
    from kafka.errors import KafkaError
except ImportError:
    print("❌ kafka-python not installed!")
    print("Run: pip install kafka-python")
    sys.exit(1)

# Configuration
KAFKA_BROKER = os.getenv('KAFKA_BROKER', 'localhost:9092')
TOPICS = ['nepse-live-prices', 'nepse-top-gainers', 'nepse-top-losers', 'nepse-market-summary']

running = True

def signal_handler(sig, frame):
    """Handle Ctrl+C gracefully"""
    global running
    print("\n\n🛑 Shutting down dashboard...")
    running = False

signal.signal(signal.SIGINT, signal_handler)


class LiveDashboard:
    """Real-time NEPSE dashboard"""
    
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
        """Connect to Kafka"""
        print(f"📡 Connecting to Kafka broker: {self.broker}")
        try:
            self.consumer = KafkaConsumer(
                *TOPICS,
                bootstrap_servers=[self.broker],
                value_deserializer=lambda m: json.loads(m.decode('utf-8')),
                auto_offset_reset='latest',  # Start from latest
                enable_auto_commit=True,
                group_id='nepse-dashboard'
            )
            print("✅ Connected to Kafka!")
            print(f"📋 Subscribed to topics: {', '.join(TOPICS)}")
            return True
        except Exception as e:
            print(f"❌ Failed to connect to Kafka: {e}")
            print("Make sure Kafka is running and streamer is publishing data")
            return False
    
    def format_price(self, price):
        """Format price with color"""
        try:
            return f"Rs. {float(price):,.2f}"
        except:
            return "N/A"
    
    def format_change(self, change):
        """Format change with color indicator"""
        try:
            change_val = float(change)
            if change_val > 0:
                return f"🟢 +{change_val:.2f}%"
            elif change_val < 0:
                return f"🔴 {change_val:.2f}%"
            else:
                return f"⚪ {change_val:.2f}%"
        except:
            return "N/A"
    
    def display_stock_update(self, stock):
        """Display a single stock update"""
        symbol = stock.get('symbol', 'N/A')
        ltp = self.format_price(stock.get('lastTradedPrice'))
        change = self.format_change(stock.get('percentageChange'))
        volume = stock.get('totalTradeQuantity', 0)
        
        print(f"  📈 {symbol:8s} | {ltp:15s} | {change:15s} | Vol: {volume:,}")
    
    def display_gainers(self, data):
        """Display top gainers"""
        print("\n" + "=" * 70)
        print("🟢 TOP 10 GAINERS")
        print("=" * 70)
        
        gainers = data.get('gainers', [])
        for i, stock in enumerate(gainers[:10], 1):
            symbol = stock.get('symbol', 'N/A')
            change = stock.get('percentageChange', 0)
            ltp = self.format_price(stock.get('lastTradedPrice'))
            print(f"{i:2d}. {symbol:8s} | {ltp:15s} | +{change:.2f}%")
    
    def display_losers(self, data):
        """Display top losers"""
        print("\n" + "=" * 70)
        print("🔴 TOP 10 LOSERS")
        print("=" * 70)
        
        losers = data.get('losers', [])
        for i, stock in enumerate(losers[:10], 1):
            symbol = stock.get('symbol', 'N/A')
            change = stock.get('percentageChange', 0)
            ltp = self.format_price(stock.get('lastTradedPrice'))
            print(f"{i:2d}. {symbol:8s} | {ltp:15s} | {change:.2f}%")
    
    def display_summary(self, summary):
        """Display market summary"""
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
    
    def run(self, mode: str = 'compact'):
        """
        Run the dashboard
        
        Args:
            mode: 'compact' (summary updates) or 'verbose' (all updates)
        """
        if not self.connect():
            return
        
        print("\n" + "=" * 70)
        print("⚡ NEPSE LIVE STOCK DASHBOARD")
        print("=" * 70)
        print(f"Mode: {mode}")
        print("Waiting for live data from Kafka...")
        print("Press Ctrl+C to stop")
        print("=" * 70)
        
        last_summary_display = 0
        summary_display_interval = 5  # Show summary every 5 seconds
        
        try:
            for message in self.consumer:
                if not running:
                    break
                
                topic = message.topic
                data = message.value
                
                self.stats['messages_received'] += 1
                self.stats['by_topic'][topic] += 1
                
                # Handle different topics
                if topic == 'nepse-live-prices':
                    symbol = data.get('symbol')
                    if symbol:
                        self.latest_data['stocks'][symbol] = data
                    
                    # In verbose mode, show each update
                    if mode == 'verbose':
                        self.display_stock_update(data)
                
                elif topic == 'nepse-top-gainers':
                    self.latest_data['gainers'] = data.get('gainers', [])
                    if mode == 'verbose':
                        self.display_gainers(data)
                
                elif topic == 'nepse-top-losers':
                    self.latest_data['losers'] = data.get('losers', [])
                    if mode == 'verbose':
                        self.display_losers(data)
                
                elif topic == 'nepse-market-summary':
                    self.latest_data['summary'] = data
                    
                    # Show summary periodically in compact mode
                    current_time = datetime.now().timestamp()
                    if mode == 'compact' and (current_time - last_summary_display) >= summary_display_interval:
                        print(f"\n⏰ {datetime.now().strftime('%H:%M:%S')} - Live Update")
                        self.display_summary(data)
                        
                        # Show top 5 gainers and losers
                        if self.latest_data['gainers']:
                            print("\n🟢 Top 5 Gainers:")
                            for i, stock in enumerate(self.latest_data['gainers'][:5], 1):
                                symbol = stock.get('symbol', 'N/A')
                                change = stock.get('percentageChange', 0)
                                ltp = self.format_price(stock.get('lastTradedPrice'))
                                print(f"  {i}. {symbol:8s} | {ltp:15s} | +{change:.2f}%")
                        
                        if self.latest_data['losers']:
                            print("\n🔴 Top 5 Losers:")
                            for i, stock in enumerate(self.latest_data['losers'][:5], 1):
                                symbol = stock.get('symbol', 'N/A')
                                change = stock.get('percentageChange', 0)
                                ltp = self.format_price(stock.get('lastTradedPrice'))
                                print(f"  {i}. {symbol:8s} | {ltp:15s} | {change:.2f}%")
                        
                        print("\n" + "-" * 70)
                        print(f"📊 Messages received: {self.stats['messages_received']}")
                        print("-" * 70)
                        
                        last_summary_display = current_time
        
        except KeyboardInterrupt:
            pass
        
        finally:
            self.cleanup()
    
    def cleanup(self):
        """Cleanup resources"""
        print("\n" + "=" * 70)
        print("📊 SESSION STATISTICS")
        print("=" * 70)
        print(f"Total messages: {self.stats['messages_received']}")
        print("\nBy topic:")
        for topic, count in self.stats['by_topic'].items():
            print(f"  {topic}: {count}")
        print("=" * 70)
        
        if self.consumer:
            self.consumer.close()
            print("✅ Kafka connection closed")


def main():
    """Main entry point"""
    print("\n🚀 Starting NEPSE Live Dashboard...")
    
    # Get mode from command line
    mode = 'compact'  # Default
    if len(sys.argv) > 1:
        if sys.argv[1] in ['compact', 'verbose']:
            mode = sys.argv[1]
        else:
            print(f"Invalid mode. Using default: {mode}")
            print("Valid modes: compact, verbose")
    
    dashboard = LiveDashboard(broker=KAFKA_BROKER)
    dashboard.run(mode=mode)


if __name__ == "__main__":
    main()
