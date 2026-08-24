import time
import os
import sqlite3
import pandas as pd
import MetaTrader5 as mt5
from datetime import datetime

# Local Module Imports
import config
import data_loader
from features.factory import add_v1_features
import risk_manager
import execution_bridge
import trading_logic
import regime_detector
from models.ensemble import EnsembleEngine

# Prioritized Instruments
ASSETS = ['AUDNZD', 'BTCUSD', 'AUDUSD', 'EURJPY', 'CADJPY', 'NZDCAD', 'AUDCAD', 'EURUSD', 'GBPSGD', 'GBPCAD']
DB_PATH = os.path.join("database", "market.db")

def log_trade_to_db(data):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        query = "INSERT INTO trades (symbol, direction, price, lots, drawdown_at_entry, mode) VALUES (?, ?, ?, ?, ?, ?)"
        cursor.execute(query, (data["symbol"], data["direction"], data["price"], data["lots"], data["drawdown"], data["mode"]))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"[DB ERROR] {e}")

def main_loop():
    print("=== AI ENSEMBLE EA: PRODUCTION ENGINE ACTIVE ===")
    risk = risk_manager.RiskManager(max_dd_limit=0.25)
    bridge = execution_bridge.MT5ExecutionBridge(risk_manager=risk)
    detector = regime_detector.RegimeDetector()
    logic = trading_logic.TradingLogic(risk_manager=risk)
    ensemble = EnsembleEngine(models_dir="models/")

    last_trade_time = time.time()
    HEARTBEAT_LIMIT = 9.5 * 24 * 3600  # 9.5 Days

    while True:
        current_time = time.time()

        # 1. Heartbeat Activity Trade
        if (current_time - last_trade_time) > HEARTBEAT_LIMIT:
            print("[HEARTBEAT] Forcing activity trade to prevent disqualification...")
            status = bridge.execute_signal(ASSETS[0], 99, 0, 0.99, trade_sizing_multiplier=0.01)
            if status == "ORDER_SENT": last_trade_time = current_time

        # 2. Asset Rotation
        for symbol in ASSETS:
            try:
                # Fetch & Preprocess
                df = data_loader.fetch_historical_data(symbol, "M15", 60)
                if df.empty: continue
                
                df = add_v1_features(df)
                regime = detector.detect(df)
                
                # Ensemble Inference (2/3 Majority Vote)
                X_input = df.iloc[[-1]].drop(columns=['time', 'tick_volume'], errors='ignore')
                ensemble_multiplier = ensemble.get_consensus_multiplier(X_input)
                
                if ensemble_multiplier <= 0: continue

                # Account State
                equity, util = bridge.get_account_info()
                if equity is None: continue

                # Adaptive Strategy Execution
                logic_multiplier = logic.evaluate_entry(symbol, 80, regime, equity)
                final_multiplier = logic_multiplier * ensemble_multiplier

                if final_multiplier > 0:
                    status = bridge.execute_signal(symbol, 80, df['close'].iloc[-1], 0.7, final_multiplier)
                    if status == "ORDER_SENT":
                        print(f"[EXECUTION] Signal Sent for {symbol} | Confidence High")
                        last_trade_time = current_time
                        log_trade_to_db({
                            "symbol": symbol, "direction": "BUY", "price": df['close'].iloc[-1],
                            "lots": final_multiplier * 0.1, "drawdown": risk.current_drawdown, "mode": logic.mode
                        })

            except Exception as e:
                print(f"[CYCLE ERROR] {symbol}: {e}")

        time.sleep(15)

if __name__ == '__main__':
    main_loop()