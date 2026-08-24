import time
import os
import pandas as pd
import joblib
import config
import data_loader
import features
import risk_manager
import execution_bridge
import model_factory
import trading_logic
import regime_detector
import probability_estimator


def retrain_model(symbols, timeframe):
    print(f"\n[AI TRAINING] Aggregating multi-asset data for retraining...")
    all_data = []
    for symbol in symbols:
        df = data_loader.fetch_historical_data(symbol=symbol, timeframe=timeframe, limit=200)
        if not df.empty:
            df = features.add_technical_features(df)
            df['target'] = (df['close'].shift(-3) > df['close']).astype(int)
            all_data.append(df)

    if not all_data:
        return None

    combined_df = pd.concat(all_data).dropna(subset=['rsi_14', 'macd', 'bb_upper', 'bb_lower', 'target'])
    feature_cols = ['rsi_14', 'macd', 'bb_upper', 'bb_lower']

    factory = model_factory.ModelFactory()
    model = factory.get_xgb_baseline()
    model.fit(combined_df[feature_cols], combined_df['target'])

    model_save_path = os.path.join(project_root, config.AI_MODEL_PATH)
    joblib.dump(model, model_save_path)
    print(f"[AI TRAINING] Fresh model trained and saved.")
    return model

def main_loop():
    print(f"AI EA Started | Continuous Retraining & Trading Active")
    risk = risk_manager.RiskManager(max_dd_limit=config.MAX_DD_LIMIT)
    bridge = execution_bridge.MT5ExecutionBridge(risk_manager=risk)
    detector = regime_detector.RegimeDetector()
    logic = trading_logic.TradingLogic()

    last_train_time = 0

    while True:
        current_time = time.time()

        # Retrain every 2 minutes
        if current_time - last_train_time > 120:
            retrain_model(config.INSTRUMENTS, config.TIMEFRAME)
            last_train_time = current_time
            # Reload probability engine with new model
            prob_engine = probability_estimator.ProbabilityEstimator(model_path=os.path.join(project_root, config.AI_MODEL_PATH))

        for symbol in config.INSTRUMENTS:
            try:
                df = data_loader.fetch_historical_data(symbol=symbol, timeframe=config.TIMEFRAME, limit=50)
                if df.empty: continue
                df = features.add_technical_features(df)

                # Inference & Trading Execution
                regime = detector.detect(df)
                row = df.iloc[[-1]][['rsi_14', 'macd', 'bb_upper', 'bb_lower']]
                win_prob, _, _ = prob_engine.estimate(row)
                score = win_prob * 100

                if logic.evaluate_entry(symbol, score, regime):
                    status = bridge.execute_signal(symbol, score, df['close'].iloc[-1], win_prob)
                    if status == "ORDER_SENT":
                        print(f"Trade Executed for {symbol} at AI Confidence {score:.1f}%")

            except Exception as e:
                print(f"Cycle Error for {symbol}: {e}")

        time.sleep(15)

if __name__ == '__main__':
    main_loop()
