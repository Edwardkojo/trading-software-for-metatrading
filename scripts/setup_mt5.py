"""
Interactive MT5 setup assistant.
"""

import sys
import json
from pathlib import Path

def main() -> None:
    print("=" * 60)
    print("MetaTrader 5 Setup Assistant")
    print("=" * 60)
    print()
    
    # Check if MT5 is installed
    mt5_path = Path("C:/Program Files/MetaTrader 5/terminal64.exe")
    if not mt5_path.exists():
        print("❌ MetaTrader 5 not found at default location")
        print("   Please install MT5 first from: https://www.metatrader5.com/")
        sys.exit(1)
    
    print("✓ MetaTrader 5 is installed")
    print()
    
    # Check if MT5 is running
    try:
        import MetaTrader5 as mt5
        if mt5.initialize():
            print("✓ MT5 terminal is running and connected")
            account_info = mt5.account_info()
            if account_info:
                print(f"✓ Logged in as: {account_info.login}")
                print(f"  Server: {account_info.server}")
                print(f"  Balance: {account_info.balance}")
                mt5.shutdown()
                
                # Update config
                config_path = Path("config/default.json")
                if config_path.exists():
                    with open(config_path, "r") as f:
                        config = json.load(f)
                    
                    config["use_mt5"] = True
                    if not config.get("mt5"):
                        config["mt5"] = {}
                    
                    config["mt5"]["login"] = account_info.login
                    config["mt5"]["server"] = account_info.server
                    
                    print()
                    print("📝 Updating config/default.json...")
                    print(f"   Login: {account_info.login}")
                    print(f"   Server: {account_info.server}")
                    print()
                    print("⚠️  You still need to add your password manually!")
                    print("   Edit config/default.json and add your password")
                    
                    with open(config_path, "w") as f:
                        json.dump(config, f, indent=2)
                    
                    print()
                    print("✅ Config updated! Add your password and you're ready to go.")
                else:
                    print("⚠️  config/default.json not found")
            else:
                print("⚠️  MT5 is running but not logged in")
                print("   Please log in through the MT5 terminal first")
        else:
            error = mt5.last_error()
            print(f"❌ MT5 connection failed: {error}")
            print()
            print("📋 Setup Steps:")
            print("   1. Open MetaTrader 5 terminal (should open automatically)")
            print("   2. Log in to your account:")
            print("      - File → Login to Trade Account")
            print("      - Enter your login, password, and server")
            print("   3. Enable automated trading:")
            print("      - Tools → Options → Expert Advisors")
            print("      - Check 'Allow automated trading'")
            print("   4. Run this script again: python scripts/setup_mt5.py")
    except ImportError:
        print("❌ MetaTrader5 Python package not installed")
        print("   Install with: pip install MetaTrader5")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}")
        print()
        print("📋 Manual Setup Steps:")
        print("   1. Open MetaTrader 5 terminal")
        print("   2. Log in to your account")
        print("   3. Enable automated trading (Tools → Options → Expert Advisors)")
        print("   4. Edit config/default.json with your credentials")
        print("   5. Run: python scripts/test_mt5_connection.py")


if __name__ == "__main__":
    main()

