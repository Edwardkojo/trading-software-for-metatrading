# MetaTrader 5 Setup Guide

This guide will help you set up MetaTrader 5 for use with the trading bot.

## Prerequisites

1. **MetaTrader 5 Terminal** - Download and install from your broker or [MetaQuotes website](https://www.metatrader5.com/)
2. **Trading Account** - You need a demo or live trading account
3. **Python MetaTrader5 Package** - Already included in requirements.txt

## Step-by-Step Setup

### 1. Install MetaTrader 5

- Download MT5 from your broker or the official MetaQuotes website
- Install and launch the terminal
- Complete the initial setup wizard

### 2. Log In to Your Account

1. Open MetaTrader 5 terminal
2. Click **File → Login to Trade Account**
3. Enter your credentials:
   - **Login**: Your account number (numeric, e.g., `12345678`)
   - **Password**: Your trading password
   - **Server**: Your broker's server name
4. Click **Login**

### 3. Enable Automated Trading

1. In MT5 terminal, go to **Tools → Options**
2. Click the **Expert Advisors** tab
3. Check the following:
   - ✅ **Allow automated trading**
   - ✅ **Allow DLL imports** (if needed)
   - ✅ **Allow external experts imports**
4. Click **OK**

### 4. Verify Connection

Run the diagnostic script:

```bash
python scripts/diagnose_mt5.py
```

You should see:
- ✓ MT5 initialized successfully
- Account info with your login and balance
- Available symbols (EURUSD, etc.)

### 5. Update Configuration

Edit `config/default.json`:

```json
{
  "use_mt5": true,
  "mt5": {
    "login": 12345678,
    "password": "your_password",
    "server": "YourBroker-Demo",
    "deviation": 10
  }
}
```

**Important Notes:**
- `login` must be a **number** (integer), not a string
- Use your actual account number from MT5
- Server name must match exactly what's shown in MT5 terminal

### 6. Test Connection

```bash
python scripts/test_mt5_connection.py
```

## Troubleshooting

### Error: "Terminal: Authorization failed" (-6)

**Causes:**
- MT5 terminal is not running
- Not logged in to any account
- Python API cannot connect to terminal

**Solutions:**
1. Make sure MT5 terminal is open and running
2. Log in to your account in the terminal first
3. Restart MT5 terminal if needed
4. Run `python scripts/diagnose_mt5.py` for detailed diagnostics

### Error: "Terminal not found" (-1)

**Causes:**
- MT5 is not installed
- MT5 is installed in a non-standard location

**Solutions:**
1. Install MetaTrader 5
2. Make sure it's in the default installation path
3. Restart your computer after installation

### Error: "Invalid login" or "Invalid password"

**Causes:**
- Wrong credentials in config file
- Login format is incorrect (should be integer)

**Solutions:**
1. Verify credentials in MT5 terminal first
2. Make sure `login` in config is a number, not a string
3. Check server name matches exactly

### Error: "Trade is disabled"

**Causes:**
- Automated trading is not enabled in MT5

**Solutions:**
1. Go to **Tools → Options → Expert Advisors**
2. Enable **Allow automated trading**
3. Restart MT5 terminal

## Using Demo vs Live Account

### Demo Account (Recommended for Testing)
- Free to create
- Uses virtual money
- Perfect for testing strategies
- No risk to real funds

### Live Account
- Uses real money
- Requires deposit
- Higher risk
- Only use after thorough testing

**Recommendation:** Start with a demo account to test everything works, then switch to live when ready.

## Security Best Practices

1. **Never commit credentials** - `config/default.json` is already gitignored
2. **Use environment variables** for sensitive data:
   ```bash
   export TRADIN_MT5_LOGIN=12345678
   export TRADIN_MT5_PASSWORD=your_password
   export TRADIN_MT5_SERVER=YourBroker-Demo
   ```
3. **Use demo account first** - Test thoroughly before going live
4. **Monitor your bot** - Don't leave it unattended initially

## Next Steps

Once MT5 is connected:
1. Run `python scripts/test_mt5_connection.py` to verify
2. Start with paper trading: `python scripts/run_bot.py`
3. Monitor the logs in `logs/` directory
4. Check trade history in `logs/trades.db`

## Additional Resources

- [MetaTrader 5 Python API Documentation](https://www.mql5.com/en/docs/integration/python_metatrader5)
- [MetaTrader 5 Help Center](https://www.metatrader5.com/en/support)

