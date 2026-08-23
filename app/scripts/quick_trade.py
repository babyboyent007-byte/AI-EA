import sys
import os
from pathlib import Path

# Path Alignment
APP_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(APP_DIR))

from execution.bridge import MT5ExecutionBridge
from risk.risk_manager import RiskManager

def execute_immediate_trade(symbol='EURUSD', direction='BUY'):
    print(f"🚀 Initializing Immediate Trade: {direction} {symbol}")
    
    # Core logic bypass for manual override/test
    risk = RiskManager(max_dd_limit=0.25)
    bridge = MT5ExecutionBridge(risk_manager=risk)
    
    # Simulated win_prob to force authorization (0.95)
    status = bridge.execute(symbol, 0.95 if direction == 'BUY' else 0.05, 1.1050)
    print(f"RESULT: {status}")

if __name__ == '__main__':
    execute_immediate_trade()