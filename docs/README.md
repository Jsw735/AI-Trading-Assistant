# AI Trading Assistant - Project Structure

## Overview
Python-based AI trading signal generation and analysis tool. Fetches real-time market data, calculates composite trading scores, and outputs actionable signals to Excel.

## Folder Structure

```
AI-Trading-Assistant/
├── config/
│   └── default_config.json       # Main configuration (editable)
├── data/
│   ├── inputs/                   # Input data (watchlists, symbols)
│   └── outputs/                  # Generated Excel reports
├── src/
│   ├── __init__.py
│   ├── main.py                   # Entry point
│   ├── core/
│   │   ├── __init__.py
│   │   └── scoring.py            # Signal scoring logic
│   ├── fetchers/
│   │   ├── __init__.py
│   │   └── data_fetcher.py       # API data retrieval
│   ├── processors/
│   │   ├── __init__.py
│   │   └── signal_processor.py   # Signal generation & ranking
│   └── utils/
│       ├── __init__.py
│       ├── logger.py             # Logging configuration
│       └── excel_writer.py       # Excel output generation
├── tests/
│   ├── unit/
│   │   ├── test_scoring.py
│   │   └── ...
│   └── integration/
│       ├── test_integration.py
│       └── ...
├── templates/                    # Excel templates (if needed)
├── docs/                         # Documentation
├── logs/                         # Application logs
├── README.md
├── requirements.txt              # Python dependencies
└── .gitignore
```

## Key Components

### Configuration (`config/default_config.json`)
Centralized parameters covering:
- **Account**: Capital, position sizing, risk limits
- **Filters**: Price range, volume, market cap, float
- **Signals**: Momentum, RSI, volume surge, relative strength
- **Instruments**: Equities, options, crypto selection
- **News/Catalysts**: Sentiment weights, keyword filters
- **Alerts**: Email, score thresholds
- **Data Sources**: API keys and preferences

### Core Logic (`src/core/scoring.py`)
Scoring engine that combines:
- **Momentum** (RSI-based, 25% weight)
- **Volume Surge** (20-day avg comparison, 20% weight)
- **Relative Strength** (vs sector ETF, 20% weight)
- **News Sentiment** (positive article ratio, 20% weight)
- **Catalysts** (recency + keyword match, 15% weight)

**Final Score = 0–100 (higher = stronger signal)**

### Data Fetching (`src/fetchers/data_fetcher.py`)
Handles integration with external APIs:
- Price/volume: Polygon, Alpaca, E*TRADE
- News/catalysts: Finnhub, Benzinga
- Fundamentals: Financial Modeling Prep
- Sector data: ETF prices (XLK, XLF, etc.)

### Signal Processing (`src/processors/signal_processor.py`)
Generates and ranks signals:
1. Filter by criteria (price, volume, market cap, float)
2. Calculate composite scores
3. Rank by score
4. Apply risk controls
5. Return top N signals

### Excel Output (`src/utils/excel_writer.py`)
Multi-sheet workbook:
- **Dashboard**: Summary metrics, top picks
- **Signals**: Ranked list with scores & components
- **News**: Catalyst summaries
- **Parameters**: Editable configuration
- **Logs**: Data refresh status
- **History Report**: Trade history (overwritten each refresh)

## Workflow

```
SCHEDULED TRIGGER (every 5 min) OR MANUAL RUN
    ↓
Load Parameters (from JSON + Excel Parameters sheet)
    ↓
Fetch Data (prices, volume, news, fundamentals, sector)
    ↓
Generate Signals (apply scoring logic)
    ↓
Filter & Rank (apply all constraints)
    ↓
Generate Excel (write all sheets)
    ↓
Send Alerts (if score > threshold)
    ↓
Log Status & Complete
```

## Getting Started

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure API Keys
Edit `config/default_config.json` and add your API keys:
```json
"polygon_api_key": "YOUR_KEY",
"finnhub_api_key": "YOUR_KEY"
```

### 3. Run the Program
```bash
python src/main.py
```

Output will be saved to `data/outputs/trading_signals.xlsx`

### 4. Edit Parameters
- Open `trading_signals.xlsx` → Parameters sheet
- Modify thresholds as needed
- Next run will read updated values

## Testing

### Run Unit Tests
```bash
python -m pytest tests/unit/
```

### Run Integration Tests
```bash
python -m pytest tests/integration/
```

## Data Sources & Budget

| Service | Cost | Purpose |
|---------|------|---------|
| E*TRADE / Interactive Brokers | Free (with account) | Equities + options |
| Polygon.io | $29/mo | Real-time + crypto |
| Finnhub | $99/mo | News + fundamentals |
| Financial Modeling Prep | $29/mo | Deeper financials |
| **Total** | ~**$130–160/mo** | Full stack |

## Configuration Parameters

### Account Settings
- `total_capital`: $1,000 (starting account)
- `position_size`: $50 (per trade)
- `max_loss_per_trade_pct`: 1.0%
- `max_daily_loss_pct`: 3.0%

### Filter Thresholds
- Price: $5–$200
- Avg Volume: > 1M shares
- Market Cap: > $500M
- Float: < 200M shares

### Signal Weights
- Momentum: 25%
- Volume: 20%
- Relative Strength: 20%
- News Sentiment: 20%
- Catalysts: 15%

### Refresh Schedule
- Interval: Every 5 minutes (configurable)
- Market Hours: 9:30 AM–4:00 PM ET
- Pre-Market: 7:00 AM start
- Manual run anytime

## Common Customizations

### Change Score Weights
Edit `src/core/scoring.py` → `self.weights` dict

### Add New Filter
Update `src/processors/signal_processor.py` → `apply_filters()` method

### Add New Data Source
Extend `src/fetchers/data_fetcher.py` with new fetch methods

### Modify Alert Frequency
Update `config/default_config.json` → `alerts.alert_frequency`

## Troubleshooting

### "API Key Invalid"
- Check that API keys in `config/default_config.json` are correct
- Verify API account is active and has sufficient credits

### "No signals generated"
- Check filter thresholds (may be too strict)
- Verify market data is being fetched (check logs)
- Ensure symbols in watchlist are valid

### "Excel file locked"
- Close the file if already open
- Wait a few seconds and try again

## Future Enhancements

- [ ] Real-time dashboard UI (web/desktop)
- [ ] Backtesting engine
- [ ] Position tracking & P&L
- [ ] Advanced ML scoring
- [ ] Mobile alerts
- [ ] Multi-account support
