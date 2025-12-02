#!/usr/bin/env python3
"""
NEPSE Live Stock Dashboard
Consumes one or more Kafka topics (default: `nepse-stream`) and displays live updates in the terminal.

Features:
- Configurable `KAFKA_BROKER` and `TOPICS` via environment variables
- Polled consumer loop with graceful Ctrl+C shutdown using `consumer.wakeup()`
- Rich-based table rendering
"""

import os
import json
import signal
from datetime import datetime
from typing import Dict, List

from kafka import KafkaConsumer
from kafka.errors import KafkaError
from rich.console import Console
from rich.table import Table
from rich.live import Live

# Configuration
KAFKA_BROKER = os.getenv("KAFKA_BROKER", "localhost:9092")
# TOPICS can be a comma-separated list, default to `nepse-stream`
TOPICS = os.getenv("TOPICS", "nepse-stream")
POLL_TIMEOUT_MS = int(os.getenv("DASHBOARD_POLL_MS", "1000"))
REFRESH_RATE = int(os.getenv("DASHBOARD_REFRESH_PER_SECOND", "2"))

console = Console()


class NEPSELiveDashboard:
    def __init__(self, broker: str = KAFKA_BROKER, topics: str = TOPICS):
        self.broker = broker
        # support comma-separated topic list
        self.topics = [t.strip() for t in topics.split(",") if t.strip()]
        self.consumer: KafkaConsumer = None
        self.stocks: Dict[str, Dict] = {}
        self.running = True

    def connect(self):
        console.print(f"📡 Connecting to Kafka broker: {self.broker}")
        console.print(f"📋 Subscribing to topics: {', '.join(self.topics)}\n")
        try:
            self.consumer = KafkaConsumer(
                *self.topics,
                bootstrap_servers=[self.broker],
                value_deserializer=lambda m: json.loads(m.decode("utf-8")),
                auto_offset_reset="latest",
                enable_auto_commit=True,
                group_id="nepse-dashboard",
            )
            console.print("✅ Connected to Kafka!\n", style="bold green")
            return True
        except Exception as e:
            console.print(f"❌ Failed to create Kafka consumer: {e}", style="bold red")
            return False

    def stop(self):
        """Stop the dashboard and wake the consumer if needed."""
        self.running = False
        try:
            if self.consumer:
                # Interrupt any blocking `poll()`
                self.consumer.wakeup()
        except Exception:
            pass

    def update_stock(self, data: Dict):
        symbol = data.get("symbol")
        if symbol:
            self.stocks[symbol] = data

    def render_table(self) -> Table:
        table = Table(title=f"NEPSE Live Stock Dashboard ({len(self.stocks)} symbols)")
        table.add_column("Symbol", justify="left", style="cyan", no_wrap=True)
        table.add_column("Last Price", justify="right", style="yellow")
        table.add_column("% Change", justify="right")
        table.add_column("Volume", justify="right")

        # sort by percentageChange (desc)
        sorted_stocks = sorted(
            self.stocks.values(),
            key=lambda x: float(x.get("percentageChange", 0) or 0),
            reverse=True,
        )

        for stock in sorted_stocks[:50]:
            symbol = stock.get("symbol", "N/A")
            price = stock.get("lastTradedPrice")
            change = stock.get("percentageChange", 0)
            vol = stock.get("totalTradeQuantity", 0)

            # Safe formatting
            try:
                price_str = f"{float(price):,.2f}"
            except Exception:
                price_str = str(price or "N/A")

            try:
                change_val = float(change)
                if change_val > 0:
                    change_str = f"[green]+{change_val:.2f}%[/green]"
                elif change_val < 0:
                    change_str = f"[red]{change_val:.2f}%[/red]"
                else:
                    change_str = f"{change_val:.2f}%"
            except Exception:
                change_str = str(change)

            try:
                vol_str = f"{int(vol):,}"
            except Exception:
                vol_str = str(vol or "N/A")

            table.add_row(symbol, price_str, change_str, vol_str)

        return table

    def run(self):
        if not self.connect():
            return

        console.print("Press Ctrl+C to stop\n", style="bold yellow")

        # register a signal handler that calls the instance stop (so consumer.wakeup() is available)
        def _handler(sig, frame):
            console.print("\n🛑 Shutting down dashboard...", style="bold red")
            self.stop()

        original_handler = signal.signal(signal.SIGINT, _handler)

        try:
            with Live(self.render_table(), refresh_per_second=REFRESH_RATE, console=console) as live:
                while self.running:
                    try:
                        records = self.consumer.poll(timeout_ms=POLL_TIMEOUT_MS)
                        if not records:
                            continue

                        for tp, msgs in records.items():
                            for message in msgs:
                                try:
                                    data = message.value
                                    if isinstance(data, dict):
                                        self.update_stock(data)
                                except Exception:
                                    # ignore malformed messages
                                    continue

                        # update display after batch
                        live.update(self.render_table())

                    except KafkaError as ke:
                        console.print(f"Kafka error: {ke}", style="bold red")
                        break
                    except Exception as e:
                        # Poll may be interrupted by wakeup when stopping
                        if not self.running:
                            break
                        console.print(f"Unexpected error: {e}", style="bold red")
                        break

        finally:
            # restore original signal handler
            try:
                signal.signal(signal.SIGINT, original_handler)
            except Exception:
                pass
            # cleanup
            try:
                if self.consumer:
                    self.consumer.close()
            except Exception:
                pass
            console.print("\n✅ Kafka connection closed", style="bold green")


def main():
    dashboard = NEPSELiveDashboard()
    dashboard.run()


if __name__ == "__main__":
    main()
