"""
Configure MT5 terminal settings programmatically.
This script helps enable automated trading and other required settings.
"""

import winreg
import os
from pathlib import Path

def get_mt5_data_path():
    """Find MT5 data directory."""
    possible_paths = [
        Path(os.environ.get("APPDATA", "")) / "MetaQuotes" / "Terminal",
        Path(os.environ.get("LOCALAPPDATA", "")) / "MetaQuotes" / "Terminal",
    ]
    
    for base_path in possible_paths:
        if base_path.exists():
            # Find the most recent terminal instance
            terminals = list(base_path.glob("*"))
            if terminals:
                return max(terminals, key=lambda p: p.stat().st_mtime if p.is_dir() else 0)
    return None

def enable_automated_trading():
    """Enable automated trading in MT5 settings."""
    try:
        # MT5 stores settings in registry
        key_path = r"SOFTWARE\MetaQuotes\Terminal"
        
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_READ)
            winreg.CloseKey(key)
            print("✓ Found MT5 registry settings")
        except FileNotFoundError:
            print("⚠️  MT5 registry settings not found")
            print("   This is normal if MT5 hasn't been configured yet")
            return False
        
        print("📝 Note: Automated trading must be enabled manually in MT5:")
        print("   1. Open MT5 terminal")
        print("   2. Go to: Tools → Options → Expert Advisors")
        print("   3. Check: 'Allow automated trading'")
        print("   4. Click OK")
        return True
        
    except Exception as e:
        print(f"⚠️  Could not access registry: {e}")
        return False

def main():
    print("=" * 60)
    print("MT5 Settings Configuration Helper")
    print("=" * 60)
    print()
    
    mt5_path = get_mt5_data_path()
    if mt5_path:
        print(f"✓ Found MT5 data directory: {mt5_path}")
    else:
        print("⚠️  Could not find MT5 data directory")
        print("   This is normal if MT5 hasn't been used yet")
    
    print()
    print("📋 Manual Configuration Steps:")
    print()
    print("1. ENABLE AUTOMATED TRADING:")
    print("   - In MT5 terminal: Tools → Options")
    print("   - Click 'Expert Advisors' tab")
    print("   - Check ✅ 'Allow automated trading'")
    print("   - Check ✅ 'Allow DLL imports' (optional)")
    print("   - Click OK")
    print()
    print("2. VERIFY CONNECTION:")
    print("   Run: python scripts/diagnose_mt5.py")
    print()
    print("3. TEST CONNECTION:")
    print("   Run: python scripts/test_mt5_connection.py")
    print()
    
    enable_automated_trading()

if __name__ == "__main__":
    main()

