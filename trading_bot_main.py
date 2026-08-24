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
    print(f'\n[AI TRAINING] Aggregating data for retraining...')
    all_data = []
    project_root = 'AI-EA'
    for symbol in symbols:
        df = data_loader.fetch_historical_data(symbol=symbol, timeframe=timeframe, limit=200)
        if not df.empty:
            df = features.add_technical_features(df)
            df['target'] = (df['close'].shift(-3) > df['close']).astype(int)
            all_data.append(df)
    if not all_data: return None
    combined_df = pd.concat(all_data).dropna()
    factory = model_factory.ModelFactory()
    model = factory.get_xgb_baseline()
    model.fit(combined_df[['rsi_14', 'macd', 'bb_upper', 'bb_lower']], combined_df['target'])
    joblib.dump(model, os.path.join(project_root, config.AI_MODEL_PATH))
    print('[AI TRAINING] Fresh model saved.')
    return model

def main_loop():
    print('AI EA Started | Heartbeat & Adaptive Risk Active')
    project_root = 'AI-EA'
    risk = risk_manager.RiskManager(max_dd_limit=config.MAX_DD_LIMIT)
    bridge = execution_bridge.MT5ExecutionBridge(risk_manager=risk)
    detector = regime_detector.RegimeDetector()
    logic = trading_logic.TradingLogic(risk_manager=risk)

    last_train_time = 0
    last_trade_time = time.time()
    MAX_INACTIVITY = 9.5 * 24 * 3600 # 9.5 Days

    while True:
        current_time = time.time()
        if current_time - last_train_time > 120:
            retrain_model(config.INSTRUMENTS, config.TIMEFRAME)
            last_train_time = current_time
            prob_engine = probability_estimator.ProbabilityEstimator(model_path=os.path.join(project_root, config.AI_MODEL_PATH))

        # Heartbeat Disqualification Prevention
        if (current_time - last_trade_time) > MAX_INACTIVITY:
            print('[HEARTBEAT] Triggering activity trade to prevent disqualification.')
            status = bridge.execute_signal(config.INSTRUMENTS[0], 99, 0, 0.99, trade_sizing_multiplier=0.01)
            if status == 'ORDER_SENT': last_trade_time = current_time

        for symbol in config.INSTRUMENTS:
            try:
                df = data_loader.fetch_historical_data(symbol, config.TIMEFRAME, 50)
                if df.empty: continue
                df = features.add_technical_features(df)
                regime = detector.detect(df)
                row = df.iloc[[-1]][['rsi_14', 'macd', 'bb_upper', 'bb_lower']]
                win_prob, _, _ = prob_engine.estimate(row)

                equity, _ = bridge.get_account_info()
                if equity is None: continue

                multiplier = logic.evaluate_entry(symbol, win_prob*100, regime, equity)
                if multiplier > 0:
                    status = bridge.execute_signal(symbol, win_prob*100, df['close'].iloc[-1], win_prob, multiplier)
                    if status == 'ORDER_SENT':
                        print(f'Trade Executed for {symbol} at AI Confidence {win_prob*100:.1f}%')
                        last_trade_time = current_time
            except Exception as e:
                print(f'Loop Error for {symbol}: {e}')
        time.sleep(15)

if __name__ == '__main__':
    main_loop()