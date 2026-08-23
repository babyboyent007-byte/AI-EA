import os
import subprocess
import sys
import pandas as pd
import joblib
import config
import data_loader
import features
import model_factory

# Ensure dependencies are present locally
[subprocess.check_call([sys.executable, '-m', 'pip', 'install', m]) for m in ['joblib','matplotlib','xgboost','ccxt'] if m not in sys.modules]

def retrain_model(symbols, timeframe):
    # DYNAMIC ROOT DEFINITION: Fixes NameError in PyCharm
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = current_dir 

    print(f"\n[AI TRAINING] Aggregating multi-asset data for retraining in: {project_root}")
    all_data = []
    for symbol in symbols:
        df = data_loader.fetch_historical_data(symbol=symbol, timeframe=timeframe, limit=200)
        if not df.empty:
            df = features.add_technical_features(df)
            df['target'] = (df['close'].shift(-3) > df['close']).astype(int)
            all_data.append(df)

    if not all_data:
        return None

    combined_df = pd.concat(all_data).dropna()
    feature_cols = ['rsi_14', 'macd', 'bb_upper', 'bb_lower']

    factory = model_factory.ModelFactory()
    model = factory.get_xgb_baseline()
    model.fit(combined_df[feature_cols], combined_df['target'])

    # Use the locally resolved project_root
    model_save_path = os.path.join(project_root, 'models/competition_v1.pkl')
    os.makedirs(os.path.dirname(model_save_path), exist_ok=True)
    joblib.dump(model, model_save_path)
    print(f"[AI TRAINING] Fresh model saved to: {model_save_path}")
    return model