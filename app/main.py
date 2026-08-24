import os
import sys
import pandas as pd
import joblib
# Custom module imports
import config
import data_loader
import features
import model_factory

def retrain_model(symbols, timeframe):
    # Robust Path Detection for PyCharm and Colab
    # This points to the directory containing main.py
    project_root = os.path.dirname(os.path.abspath(__file__))
    
    print(f"\n[AI TRAINING] Environment: {project_root}")
    
    all_data = []
    for symbol in symbols:
        df = data_loader.fetch_historical_data(symbol=symbol, timeframe=timeframe, limit=200)
        if not df.empty:
            df = features.add_technical_features(df)
            df['target'] = (df['close'].shift(-3) > df['close']).astype(int)
            all_data.append(df)

    if not all_data:
        print("❌ No training data available.")
        return None

    combined_df = pd.concat(all_data).dropna()
    feature_cols = ['rsi_14', 'macd', 'bb_upper', 'bb_lower']

    factory = model_factory.ModelFactory()
    model = factory.get_xgb_baseline()
    model.fit(combined_df[feature_cols], combined_df['target'])

    # Save in a standardized 'models' subdirectory
    model_dir = os.path.join(project_root, 'models')
    os.makedirs(model_dir, exist_ok=True)
    save_path = os.path.join(model_dir, 'competition_v1.pkl')
    
    joblib.dump(model, save_path)
    print(f"✅ Model saved successfully: {save_path}")
    return model