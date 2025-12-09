# 📈 VnStock Gold & Exchange Rate Analysis

A comprehensive data engineering project for analyzing Vietnamese stock market data, gold prices, and exchange rates using Apache Airflow.

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Airflow](https://img.shields.io/badge/Airflow-2.0+-red.svg)
![Docker](https://img.shields.io/badge/Docker-Enabled-blue.svg)

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Architecture](#architecture)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [DAGs Description](#dags-description)
- [API Documentation](#api-documentation)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [License](#license)

## 🎯 Overview

This project automates the collection, processing, and analysis of financial data from the Vietnamese stock market. It includes:

- **Automated Data Collection**: Daily fetching of stock prices, technical indicators, gold prices, and exchange rates
- **Technical Analysis**: Calculation of MFI (Money Flow Index) and RSI (Relative Strength Index)
- **Visualization**: Beautiful charts and technical analysis visualizations
- **Telegram Integration**: Automated notifications and chart delivery
- **Apache Airflow**: Orchestration of ETL pipelines

## ✨ Features

### Data Collection & Processing

- ✅ Historical stock data fetching (1000+ days)
- ✅ Real-time technical indicators (MFI, RSI)
- ✅ VietcomBank exchange rates
- ✅ BTMC gold prices
- ✅ Company information extraction

### Technical Analysis

- 📊 Money Flow Index (MFI)
- 📈 Relative Strength Index (RSI)
- 📉 MACD (Moving Average Convergence Divergence)
- 📐 Bollinger Bands
- 🔄 Moving Averages (5, 10, 20, 50-day)
- 💹 Momentum Indicators

### Automation & Notifications

- 🔔 Telegram bot integration
- 📱 Automated chart delivery
- ⏰ Scheduled daily updates
- 🔄 Backfill for missing dates

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Apache Airflow                          │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │ Stock Data  │  │ MFI Index   │  │ Exchange    │        │
│  │ Collection  │  │ Calculation │  │ Rate & Gold │        │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘        │
└─────────┼─────────────────┼─────────────────┼──────────────┘
          │                 │                 │
          ▼                 ▼                 ▼
    ┌─────────────────────────────────────────────┐
    │         Data Storage (CSV Files)            │
    │  - stock_history/                           │
    │  - stock_analysis_data/                     │
    │  - exchange_rate/                           │
    │  - gold_price/                              │
    └─────────────┬───────────────────────────────┘
                  │
                  ▼
    ┌─────────────────────────────────────────────┐
    │        Visualization & Reporting            │
    │  - Technical analysis charts                │
    │  - MFI/RSI indicators                       │
    │  - Telegram notifications                   │
    └─────────────────────────────────────────────┘
```

## 📦 Prerequisites

- **Docker** & **Docker Compose** (v2.0+)
- **Python** 3.8 or higher
- **Git**
- **Telegram Bot Token** (for notifications)
- At least **4GB RAM** for Docker containers

## 🚀 Installation

### 1. Clone the Repository

```bash
git clone https://github.com/dangkien1311/VnStock-Gold-ExchangeRate-Analysis.git
cd VnStock-Gold-ExchangeRate-Analysis
```

### 2. Set Up Python Environment (Optional for local development)

```bash
# Create virtual environment
python -m venv .venv

# Activate virtual environment
# Windows
.venv\Scripts\activate
# Linux/Mac
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Configure Telegram Bot

Create `stockapi/KFinance/Key_info.json`:

```json
{
    "telegram": {
        "token": "YOUR_TELEGRAM_BOT_TOKEN",
        "channel": "YOUR_TELEGRAM_CHAT_ID"
    }
}
```

**How to get Telegram credentials:**

1. Create a bot with [@BotFather](https://t.me/BotFather)
2. Get your chat ID from [@userinfobot](https://t.me/userinfobot)

### 4. Start Airflow with Docker

```bash
# Initialize Airflow database
docker-compose up airflow-init

# Start all services
docker-compose up -d

# Check service status
docker-compose ps
```

### 5. Access Airflow UI

- **URL**: http://localhost:8080
- **Username**: `airflow`
- **Password**: `airflow`

## ⚙️ Configuration

### Stock Symbols

Edit the stock list in `dags/stock_dag.py`:

```python
stocks = ['HPG', 'VND', 'SAB', 'MBB', 'MML', 'FPT', 'TCB', 'MCH', 'VCB']
```

### Scheduling

Modify the DAG schedule in each DAG file:

```python
schedule_interval="0 18 * * 1-5"  # Every weekday at 6 PM
```

### Data Collection Period

Adjust the number of days to fetch in `dags/stock_dag.py`:

```python
number_days = 1022  # Approximately 3 years of data
```

## 📖 Usage

### Running DAGs

#### 1. **Get Stock Data** (get_data_stock)

Fetches historical stock data and calculates technical indicators:

```bash
# Via Airflow UI: Trigger DAG manually
# Or via CLI:
docker exec -it airflow-webserver airflow dags trigger get_data_stock
```

#### 2. **Stock Analysis** (Stock_analysis)

Complete analysis pipeline - fetches data, calculates indicators, and creates visualization charts:

```bash
docker exec -it airflow-webserver airflow dags trigger Stock_analysis
```

**What it does:**

- Downloads latest stock data (1000+ days history)
- Calculates MFI and RSI indicators
- Creates 3-panel technical analysis charts
- Sends charts to Telegram automatically
- Handles missing dates with automatic backfill

#### 3. **Exchange Rate** (VND_exchange_rate)

Fetches daily VietcomBank exchange rates:

```bash
docker exec -it airflow-webserver airflow dags trigger VND_exchange_rate
```

### Python API Usage

```python
from stockapi.KFinance import Kf_function as Kff

# Fetch stock history
Kff.get_stock_history('HPG', '2023-01-01', '2025-12-01')

# Calculate technical indicators
Kff.caculate_index('HPG')

# Visualize MFI and RSI
Kff.visualize_stock_indicators(['HPG', 'VNM'], '2025-12-09', days_back=30)

# Get company information
Kff.get_comInfo('HPG')

# Get exchange rates
Kff.exchange_rate('2025-12-09')

# Get gold prices
Kff.gold_price()
```

## 📁 Project Structure

```
VnStock-Gold-ExchangeRate-Analysis/
├── dags/                           # Airflow DAG definitions
│   ├── stock_dag.py               # Main stock data collection DAG
│   └── __pycache__/
├── stockapi/                       # Core application code
│   └── KFinance/
│       ├── Kf_function.py         # Data collection & processing
│       ├── Kf_index.py            # Technical indicators calculation
│       ├── Key_info.json          # Telegram credentials
│       ├── data/                  # Data storage
│       │   ├── stock_history/     # Raw stock data
│       │   ├── stock_analysis_data/ # Technical indicators
│       │   ├── stocks/            # Chart images
│       │   ├── exchange_rate/     # Exchange rate data
│       │   └── gold_price/        # Gold price data
├── logs/                          # Airflow logs
├── plugins/                       # Airflow plugins
├── docker-compose.yaml            # Docker services configuration
├── Dockerfile                     # Custom Airflow image
├── requirements.txt               # Python dependencies
└── README.md                      # This file
```

## 🤖 DAGs Description

### 1. `get_data_stock`

**Purpose**: Fetch and process stock data

**Schedule**: Manual trigger (on-demand)

**Tasks**:

1. `fetch_stock_data`: Downloads 1000+ days of historical data
2. `caculate_index_for_stocks`: Calculates MFI and RSI indicators

**Stocks**: HPG, VND, SAB, MBB, MML, FPT, TCB, MCH, VCB

### 2. `Stock_analysis`

**Purpose**: Complete stock analysis pipeline with data collection, indicator calculation, and visualization

**Schedule**: Manual trigger (on-demand)

**Tasks**:

1. `check_missing_date`: Identifies dates that need analysis since last successful run
2. `fetch_stock_data`: Downloads historical stock data (1000+ days) for the current date
3. `caculate_index_for_stocks`: Calculates MFI and RSI technical indicators
4. `visualize_index`: Creates comprehensive 3-panel visualization charts (Price, MFI, RSI) and sends to Telegram

**Task Flow**:

```
check_missing_date → fetch_stock_data → caculate_index_for_stocks → visualize_index
```

**Features**:

- Automatic detection and backfill for missing dates
- Complete data pipeline from fetching to visualization
- 3-panel technical analysis charts (Close Price, MFI, RSI)
- Color-coded overbought/oversold zones
- Automatic Telegram notification with charts
- High-resolution charts (300 DPI)

**Stocks**: HPG, VND, SAB, MBB, MML, FPT, TCB, MCH, VCB

### 3. `VND_exchange_rate`

**Purpose**: Collect VND exchange rates

**Schedule**: Manual trigger

**Tasks**:

1. `calculate_exchange_rate`: Gets VietcomBank exchange rates for the current date

## 🔧 API Documentation

### Kf_function Module

#### `get_stock_history(stock, start_date, end_date)`

Fetch historical stock data from VCI source.

**Parameters**:

- `stock` (str): Stock symbol (e.g., 'HPG')
- `start_date` (str): Start date in 'YYYY-MM-DD' format
- `end_date` (str): End date in 'YYYY-MM-DD' format

**Returns**: Saves CSV to `data/stock_history/{stock}/`

#### `caculate_index(stock)`

Calculate MFI and RSI indicators for a stock.

**Parameters**:

- `stock` (str): Stock symbol

**Returns**: Saves CSV to `data/stock_analysis_data/{stock}/`

#### `visualize_stock_indicators(stocks, date, days_back=30)`

Create technical analysis visualization.

**Parameters**:

- `stocks` (list): List of stock symbols
- `date` (str): End date in 'YYYY-MM-DD' format
- `days_back` (int): Number of days to display

**Returns**: Saves chart and sends to Telegram

## 🐛 Troubleshooting

### Common Issues

#### 1. Airflow Container Won't Start

```bash
# Check logs
docker-compose logs airflow-webserver

# Reset everything
docker-compose down -v
docker-compose up -d
```

#### 2. "Module not found" Errors

```bash
# Rebuild Docker image
docker-compose build --no-cache
docker-compose up -d
```

#### 3. Telegram Bot Not Sending Messages

- Verify bot token in `Key_info.json`
- Check if bot is added to the chat/channel
- Ensure bot has permission to send messages

#### 4. Out of Memory Errors

```yaml
# Edit docker-compose.yaml
services:
  airflow-worker:
    mem_limit: 4g  # Increase from 2g
```

## 📊 Monitoring

### Check DAG Status

```bash
# List all DAGs
docker exec -it airflow-webserver airflow dags list

# Show DAG runs
docker exec -it airflow-webserver airflow dags list-runs -d get_data_stock
```

### View Logs

```bash
# Real-time logs
docker-compose logs -f airflow-worker

# Specific task logs
docker exec -it airflow-webserver airflow tasks logs get_data_stock fetch_stock_data 2025-12-09
```

### Resource Usage

```bash
# Docker stats
docker stats

# Check disk space
docker system df
```

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### Development Guidelines

- Follow PEP 8 style guide
- Add docstrings to functions
- Include unit tests for new features
- Update documentation as needed

## 👤 Author

**Kien Dang**

- Email: kiendt.1311@gmail.com
- GitHub: [@dangkien1311](https://github.com/dangkien1311)

## 🙏 Acknowledgments

- [VnStock](https://github.com/thinh-vu/vnstock) - Vietnamese stock data API
- [Apache Airflow](https://airflow.apache.org/) - Workflow orchestration
- [TA-Lib](https://github.com/mrjbq7/ta-lib) - Technical analysis library
- [Pandas](https://pandas.pydata.org/) - Data manipulation and analysis

## 📈 Roadmap

- [ ] Add more stocks to monitoring list
- [ ] Implement real-time streaming data
- [ ] Add sentiment analysis from news
- [ ] Create web dashboard with Flask/Streamlit
- [ ] Add backtesting framework
- [ ] Implement portfolio optimization
