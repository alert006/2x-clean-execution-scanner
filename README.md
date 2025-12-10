# 2X Clean Execution Scanner

Streamlit auto scanner for EMA + Supertrend + ATR strategy on NIFTY, BANKNIFTY, and stock indices.

## Overview

This is a **real-time trading signal scanner** built with Streamlit that scans multiple symbols simultaneously for trading signals based on the "2X Clean Execution" strategy. The strategy combines:

- **EMA (Exponential Moving Average)**: Fast and slow EMAs for trend confirmation
- **Supertrend Indicator**: ATR-based dynamic support/resistance levels
- **ATR (Average True Range)**: Risk management with adaptive stop losses

## Features

✅ **Multi-Symbol Scanning**: Scan multiple symbols in one click  
✅ **Customizable Parameters**: Adjust EMA periods, ATR settings, and timeframes  
✅ **Real-Time Signals**: Buy/Sell signals with stop loss levels  
✅ **Risk Calculation**: Automatic risk in points and percentage  
✅ **Color-Coded Results**: Green for BUY, Red for SELL, Grey for no signal  
✅ **Progress Tracking**: Real-time scanning status  
✅ **NSE Market Data**: Works with NIFTY, BANKNIFTY, stocks, and indices  

## Strategy Logic

### Buy Signal
- Supertrend flips to **Uptrend** (green)
- Price closes **above Fast EMA**
- Entry at close of signal candle
- Stop Loss at **Supertrend Lower Band**

### Sell Signal  
- Supertrend flips to **Downtrend** (red)
- Price closes **below Fast EMA**
- Entry at close of signal candle
- Stop Loss at **Supertrend Upper Band**

## Installation

### Prerequisites
- Python 3.8+
- pip or conda

### Local Setup

```bash
# Clone the repository
git clone https://github.com/alert006/2x-clean-execution-scanner.git
cd 2x-clean-execution-scanner

# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run app.py
```

The scanner will open at `http://localhost:8501`

## Usage

### Step 1: Add Symbols
Enter comma-separated stock symbols in the sidebar:
```
^NSEI,^NSEBANK,HDFCBANK.NS,ICICIBANK.NS,INFY.NS,RELIANCE.NS
```

### Step 2: Configure Parameters
- **Timeframe**: Select 5m, 15m, 30m, 60m, or 1d
- **Fast EMA**: Default 9 (shorter-term trend)
- **Slow EMA**: Default 21 (medium-term trend)
- **ATR Period**: Default 10 (volatility calculation)
- **Supertrend Multiplier**: Default 3.0 (band width)

### Step 3: Click "Scan for Signals"
The scanner will:
1. Download 30 days of data for each symbol
2. Calculate EMA, Supertrend, and ATR for each
3. Generate BUY/SELL signals
4. Display results by signal type

### Step 4: Review Results
- **Green Section**: BUY signals with stop loss levels
- **Red Section**: SELL signals with stop loss levels
- **Grey Section**: No signals (neutral/choppy)

## File Structure

```
2x-clean-execution-scanner/
├── app.py                 # Main Streamlit application
├── indicators.py          # EMA, Supertrend, and signal logic
├── requirements.txt       # Python dependencies
├── README.md              # This file
└── .streamlit/
    └── config.toml        # Streamlit configuration
```

## API & Data Source

- **Data**: [yfinance](https://github.com/ranaroussi/yfinance) - Yahoo Finance
- **Symbols**: NSE symbols with `.NS` suffix (e.g., HDFCBANK.NS)
- **Indices**: Use `^NSEI` for NIFTY 50, `^NSEBANK` for BANKNIFTY

## Deployment on Streamlit Cloud

1. Push code to GitHub
2. Go to [Streamlit Cloud](https://streamlit.io/cloud)
3. Click "New App" → Select your repository
4. Choose:
   - Repository: `2x-clean-execution-scanner`
   - Branch: `main`
   - File: `app.py`
5. Deploy!

**Live App**: [https://2x-clean-execution-scanner.streamlit.app](https://2x-clean-execution-scanner.streamlit.app)

## Disclaimer

⚠️ **Educational Purpose Only**
- This scanner is for educational purposes.
- Past performance does not guarantee future results.
- Always perform your own analysis before trading.
- Use proper risk management and position sizing.
- Consult a financial advisor before making trades.

## Configuration Parameters

| Parameter | Default | Range | Description |
|-----------|---------|-------|-------------|
| Fast EMA | 9 | 1-100 | Faster trend confirmation |
| Slow EMA | 21 | 1-200 | Slower trend identification |
| ATR Period | 10 | 1-100 | Volatility lookback |
| ST Multiplier | 3.0 | 1.0-10.0 | Band width (higher = wider bands) |
| Timeframe | 15m | 5m, 15m, 30m, 60m, 1d | Candle timeframe |

## Troubleshooting

**Q: No signals found**  
A: Check if symbols are correct (use `.NS` suffix). Try longer timeframes.

**Q: "Error downloading data"**  
A: Check internet connection or symbol spelling. yfinance may have rate limits.

**Q: Streamlit app is slow**  
A: Reduce number of symbols or use longer timeframes (1h, 1d).

## Contributing

Contributions are welcome! Feel free to:
- Report bugs
- Suggest features
- Improve code
- Add new indicators

## License

MIT License - Feel free to use for personal projects.

## Author

**alert006** - Trading Strategy Developer

## Support

For issues or questions:
1. Check existing GitHub issues
2. Create a new issue with details
3. Include symbol, timeframe, and error message

---

**Happy Trading!** 📈
