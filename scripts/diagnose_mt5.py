"""
Diagnostic script to check MT5 setup and provide helpful error messages.
"""

import sys

def main() -> None:
    print("MT5 Connection Diagnostics\n" + "=" * 50)
    
    # Check if MetaTrader5 package is installed
    try:
        import MetaTrader5 as mt5
        print("✓ MetaTrader5 Python package is installed")
    except ImportError:
        print("❌ MetaTrader5 package not found")
        print("   Install with: pip install MetaTrader5")
        sys.exit(1)
    
    # Try to initialize MT5
    print("\nAttempting to initialize MT5...")
    if not mt5.initialize():
        error = mt5.last_error()
        print(f"❌ MT5 initialization failed: {error}")
        
        if error[0] == -6:
            print("\n💡 Common causes:")
            print("   1. MetaTrader 5 terminal is not running")
            print("   2. MT5 terminal is not logged in")
            print("   3. Python API cannot connect to the terminal")
            print("\n📋 Steps to fix:")
            print("   1. Open MetaTrader 5 terminal")
            print("   2. Log in to your account in the terminal")
            print("   3. Ensure 'Allow automated trading' is enabled")
            print("   4. Try running this script again")
        elif error[0] == -1:
            print("\n💡 MT5 terminal not found")
            print("   Make sure MetaTrader 5 is installed and running")
        else:
            print(f"\n💡 Error code: {error[0]}")
            print(f"   Message: {error[1]}")
        
        sys.exit(1)
    
    print("✓ MT5 initialized successfully")
    
    # Get terminal info
    terminal_info = mt5.terminal_info()
    print(f"\n📊 Terminal Info:")
    print(f"   Name: {terminal_info.name}")
    print(f"   Company: {terminal_info.company}")
    print(f"   Path: {terminal_info.path}")
    print(f"   Data Path: {terminal_info.data_path}")
    print(f"   Connected: {terminal_info.connected}")
    
    # Get account info (if logged in)
    account_info = mt5.account_info()
    if account_info:
        print(f"\n💰 Account Info:")
        print(f"   Login: {account_info.login}")
        print(f"   Server: {account_info.server}")
        print(f"   Balance: {account_info.balance}")
        print(f"   Equity: {account_info.equity}")
        print(f"   Trade Allowed: {account_info.trade_allowed}")
    else:
        print("\n⚠️  Not logged in to any account")
        print("   Log in through the MT5 terminal first")
    
    # Test symbol access
    print(f"\n🔍 Testing symbol access...")
    symbol = "EURUSD"
    symbol_info = mt5.symbol_info(symbol)
    if symbol_info:
        print(f"✓ {symbol} is available")
        tick = mt5.symbol_info_tick(symbol)
        if tick:
            print(f"   Latest tick: Bid={tick.bid}, Ask={tick.ask}")
    else:
        print(f"❌ {symbol} not found or not available")
    
    mt5.shutdown()
    print("\n✅ Diagnostics complete!")


if __name__ == "__main__":
    main()

