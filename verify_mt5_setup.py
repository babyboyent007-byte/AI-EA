import MetaTrader5 as mt5
import sys
import os

def verify_mt5():
    print("=== MT5 API HANDSHAKE TEST ===")
    
    # USER ACTION: Update these credentials locally
    LOGIN = 12345678
    PASSWORD = "YourPassword"
    SERVER = "LiteFinance-Demo"

    if not mt5.initialize():
        print(f"[ERROR] MT5 Initialization failed: {mt5.last_error()}")
        return

    if not mt5.login(LOGIN, password=PASSWORD, server=SERVER):
        print(f"[ERROR] Login failed for {LOGIN}: {mt5.last_error()}")
        mt5.shutdown()
        return

    print(f"[SUCCESS] Connected to {SERVER}")
    account_info = mt5.account_info()
    if account_info:
        print(f"  Account Login: {account_info.login}")
        print(f"  Equity: {account_info.equity} {account_info.currency}")
        print("\n[STATUS] Terminal communication established. READY.")
    
    mt5.shutdown()

if __name__ == '__main__': verify_mt5()