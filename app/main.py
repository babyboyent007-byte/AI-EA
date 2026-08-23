import sys
import os
from pathlib import Path

# Path Alignment
BASE_PATH = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_PATH))

from market.mt5_client import MT5Client
from core.event_bus import EventBus
from config import settings

def main():
    print("="*50)
    print(f" {settings.PROJECT_NAME} v0.1.0")
    print("="*50)

    print(f"Loading configuration...      OK ({settings.BASE_CURRENCY})")
    print(f"Initializing Event Bus...     OK")
    
    bus = EventBus()

    client = MT5Client(settings.SERVER, 0, "pass")
    if client.connect():
        print(f"Connecting to MT5...          OK ({settings.BROKER_NAME})")
        acc = client.get_account_info()
        print(f"Checking account...           OK (${acc['balance']})")

    print("\n✅ Core Framework initialized successfully.")

if __name__ == '__main__':
    main()