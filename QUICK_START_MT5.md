# Quick Start: MT5 Setup (5 Minutes)

## Step 1: Log In to MT5 Terminal

The MT5 terminal should now be open. If not, it's located at:
`C:\Program Files\MetaTrader 5\terminal64.exe`

**In the MT5 terminal:**

1. Click **File → Login to Trade Account**
2. Enter your credentials:
   - **Login**: Your account number (e.g., `12345678`)
   - **Password**: Your trading password
   - **Server**: Your broker's server (e.g., `MetaQuotes-Demo`)
3. Click **Login**

## Step 2: Enable Automated Trading

1. In MT5 terminal, click **Tools → Options**
2. Click the **Expert Advisors** tab
3. Check these boxes:
   - ✅ **Allow automated trading**
   - ✅ **Allow DLL imports** (optional, but recommended)
4. Click **OK**

## Step 3: Verify Setup

Run this command in your terminal:

```bash
python scripts/diagnose_mt5.py
```

You should see:
- ✓ MT5 initialized successfully
- Account info with your login number
- Available symbols

## Step 4: Update Configuration

Once logged in, run:

```bash
python scripts/setup_mt5.py
```

This will automatically detect your login and server, and update `config/default.json`.

**Then manually add your password** to `config/default.json`:

```json
{
  "mt5": {
    "login": 12345678,
    "password": "YOUR_PASSWORD_HERE",
    "server": "YourServer-Demo",
    "deviation": 10
  }
}
```

## Step 5: Test Connection

```bash
python scripts/test_mt5_connection.py
```

If successful, you'll see:
- ✓ MT5DataProvider initialized
- ✓ Latest EURUSD tick
- ✓ Account balance

## Step 6: Run the Bot!

```bash
python scripts/run_bot.py
```

## Troubleshooting

**"Terminal: Authorization failed"**
- Make sure MT5 terminal is open
- Make sure you're logged in
- Restart MT5 terminal if needed

**"Trade is disabled"**
- Go to Tools → Options → Expert Advisors
- Enable "Allow automated trading"
- Restart MT5 terminal

**"Invalid login"**
- Make sure login is a number (integer) in config
- Verify credentials in MT5 terminal first

## Need Help?

Run the diagnostic script:
```bash
python scripts/diagnose_mt5.py
```

This will show detailed information about your MT5 setup and any issues.

