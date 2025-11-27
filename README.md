# Trading AI - Automated Forex Trading Bot

A fully automated Forex trading system that connects to MetaTrader 5, runs trading strategies, manages risk, and tracks performance metrics.

## Features

- ✅ **MetaTrader 5 Integration** - Live and paper trading support
- ✅ **SMA Crossover Strategy** - Configurable fast/slow moving averages
- ✅ **Risk Management** - Max daily loss, drawdown limits, position sizing
- ✅ **Performance Metrics** - Win rate, profit factor, Sharpe ratio, drawdown tracking
- ✅ **Backtesting** - Historical strategy validation
- ✅ **Continuous Runner** - Live-loop trading with graceful shutdown
- ✅ **Trailing Stops** - Automatic stop-loss management
- ✅ **Dynamic Position Sizing** - Volatility and win-streak adjustments
- ✅ **Persistence** - SQLite database for trade history and metrics
- ✅ **Multi-Symbol Support** - Trade multiple currency pairs simultaneously

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure MT5 Credentials

Edit `config/default.json` or set environment variables:

```json
{
  "use_mt5": true,
  "mt5": {
    "login": "YOUR_LOGIN",
    "password": "YOUR_PASSWORD",
    "server": "YOUR_SERVER",
    "deviation": 10
  }
}
```

Or use environment variables:
```bash
export TRADIN_USE_MT5=1
export TRADIN_MT5_LOGIN=your_login
export TRADIN_MT5_PASSWORD=your_password
export TRADIN_MT5_SERVER=your_server
```

### 3. Test MT5 Connection

```bash
python scripts/test_mt5_connection.py
```

### 4. Run the Bot

**Paper Trading:**
```bash
python scripts/run_bot.py
```

**Backtesting:**
```bash
python scripts/run_backtest.py
```

## Configuration

Edit `config/default.json` to customize:

- `symbols`: List of currency pairs to trade (e.g., `["EURUSD", "GBPUSD"]`)
- `timeframe_minutes`: Bar timeframe (5, 15, 60, etc.)
- `poll_interval_seconds`: How often to check for new signals
- `warmup_bars`: Historical bars needed for strategy warmup
- `run_mode`: `"paper"`, `"live"`, or `"backtest"`
- `trailing_stop`: Trailing stop configuration
- `dynamic_sizing`: Position sizing adjustments

## Architecture

```
core/
    trading_engine.py    # Main orchestration
    risk_manager.py      # Risk limits and position sizing
    metrics.py           # Performance analytics
    data_handler.py      # MT5 data provider
    runner.py            # Continuous loop controller
    persistence.py       # Database and logging
    trailing_stop.py     # Trailing stop management
    position.py          # Position data structures

strategies/
    sma_crossover.py     # SMA crossover strategy

tests/                   # Full pytest test suite
scripts/                 # Utility scripts
config/                  # Configuration management
logs/                    # Trade logs and database (gitignored)
```

## Testing

Run the full test suite:

```bash
pytest
```

All tests pass with 13/13 success rate.

## GitHub Setup

To push to GitHub:

1. Create a new repository named `tradin-AI` on GitHub
2. Push the code:
   ```bash
   git push -u origin main
   ```

## Important Notes

- **Never commit `config/default.json`** - It contains credentials (already gitignored)
- **Logs directory is gitignored** - Trade history stays local
- **MT5 package is Windows-only** - For Linux/Mac, use simulated mode
- **CI runs tests only** - No MT5 installation in GitHub Actions

## License

MIT

