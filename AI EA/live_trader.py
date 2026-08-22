import time
import sys
import os
from datetime import datetime

# Add project root to path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.append(project_root)

import data_loader
import features
import regime_detector
import probability_estimator
import risk_manager
import execution_bridge

def main():
    print("==========================================")
    print("AI EA V1.0 - PRODUCTION RUNNER STARTED")
    print("Target: BTC/USDT | Frequency: 1h")
    print("==========================================")

    # Initialize components
    model_path = os.path.join(project_root, 'xgb_signal_model.pkl')
    prob_engine = probability_estimator.ProbabilityEstimator(model_path=model_path)
    risk_engine = risk_manager.RiskManager(max_dd_limit=0.25)
    detector = regime_detector.RegimeDetector()
    bridge = execution_bridge.MT5ExecutionBridge(risk_manager=risk_engine)

    while True:
        try:
            now = datetime.now()
            print(f"\n--- [Monitoring Cycle: {now.strftime('%Y-%m-%d %H:%M:%S')}] ---")
            
            # 1. Pipeline
            df = data_loader.fetch_historical_data(symbol='BTC/USDT', timeframe='1h', limit=100)
            df = features.add_technical_features(df)
            regime = detector.detect(df)
            current_price = df['close'].iloc[-1]
            
            # 2. Inference
            row = df.iloc[[-1]][['rsi_14', 'macd', 'bb_upper', 'bb_lower']]
            win_prob, _, _ = prob_engine.estimate(row)
            score = win_prob * 100

            print(f"Price: ${current_price:,.2f} | Regime: {regime} | AI Confidence: {score:.1f}%")

            # 3. Execution
            status = bridge.execute_signal('BTC/USDT', score, current_price, win_prob)
            print(f"Status: {status}")

            # 4. Wait for next candle (Hourly check)
            print("Cycle complete. Sleeping for 1 hour...")
            time.sleep(3600)
            
        except Exception as e:
            print(f"Critical loop error: {e}")
            time.sleep(60)

if __name__ == '__main__':
    main()
