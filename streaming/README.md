# 🚀 NEPSE Real-Time Stock Streaming

Professional-grade streaming system for real-time NEPSE stock market data using Apache Kafka.

## 📁 Project Structure

```
streaming/
├── README.md                    # This file  
├── requirements.txt             # Python dependencies
├── producers/                   # Kafka producers
│   └── nepse_producer.py       # Streams stock data to Kafka
├── consumers/                   # Kafka consumers
│   └── nepse_dashboard.py      # Real-time dashboard
├── docker/                      # Docker deployment
│   ├── Dockerfile
│   └── docker-compose.yml
└── scripts/                     # Utility scripts
    ├── run_in_container.sh     # Run in existing container
    └── quick_start.sh          # Quick launcher
```

## 🚀 Quick Start

```bash
cd streaming/scripts
./quick_start.sh
```

Choose: **1** for Producer, **2** for Dashboard

## 📊 What Gets Streamed

- **333+ stocks** updated every second
- **Top gainers/losers** in real-time
- **Market summary** with live statistics
- **4 Kafka topics** for different data types

## 📚 Full Documentation

See [STREAMING_GUIDE.md](STREAMING_GUIDE.md) for complete setup, configuration, and architecture details.

## 🔧 Configuration

All dependencies in `requirements.txt` - install with:
```bash
pip install -r requirements.txt
```

Environment variables:
- `KAFKA_BROKER` - Kafka address (default: `kafka:9092`)
- `STREAMING_INTERVAL` - Update interval in ms (default: `1000`)
