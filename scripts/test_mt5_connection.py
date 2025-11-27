"""
Test script to verify MT5 connection and credentials.
"""

from config import load_config
from core.data_handler import MT5DataProvider
from core.trading_engine import MT5ExecutionProvider


def main() -> None:
    config = load_config()
    
    print("Testing MT5 Connection...")
    print(f"Login: {config.mt5.login}")
    print(f"Server: {config.mt5.server}")
    print(f"Use MT5: {config.use_mt5}")
    
    try:
        # Test data provider
        print("\n1. Testing MT5DataProvider...")
        data_provider = MT5DataProvider()
        print("✓ MT5DataProvider initialized successfully")
        
        # Test fetching data
        tick = data_provider.fetch_latest_tick("EURUSD")
        print(f"✓ Latest EURUSD tick: Bid={tick.bid}, Ask={tick.ask}")
        
        # Test execution provider (requires login)
        print("\n2. Testing MT5ExecutionProvider...")
        if config.mt5.login and config.mt5.password and config.mt5.server:
            exec_provider = MT5ExecutionProvider(
                login=config.mt5.login,
                password=config.mt5.password,
                server=config.mt5.server,
                deviation=config.mt5.deviation,
            )
            print("✓ MT5ExecutionProvider initialized and logged in successfully")
            print(f"✓ Account balance: {exec_provider.mt5.account_info().balance}")
        else:
            print("⚠ MT5 credentials not configured")
            
        print("\n✅ All MT5 connection tests passed!")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()


