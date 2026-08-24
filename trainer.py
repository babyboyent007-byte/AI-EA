import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
import joblib

def train_new_model(df):
    """
    Trains a fresh AI model for the new EA project.
    Target: Predict price direction over the next few 1h candles.
    """
    if df.empty or len(df) < 100:
        print("Insufficient data to train a new model.")
        return None

    # Define features and target
    features = ['rsi_14', 'macd', 'macd_signal', 'bb_upper', 'bb_lower']
    df['target'] = np.where(df['close'].shift(-3) > df['close'], 1, 0) # 3-hour lookahead

    X = df[features].dropna()
    y = df.loc[X.index, 'target']

    # Initialize a new Random Forest for the EA
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X, y)
    
    model_path = 'new_ea_model.pkl'
    joblib.dump(model, model_path)
    print(f"Fresh AI model trained and saved as {model_path}")
    return model

if __name__ == '__main__':
    print("AI Training module for fresh EA project initialized.")
