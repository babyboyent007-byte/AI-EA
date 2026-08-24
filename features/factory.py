import sqlite3
import pandas as pd
import pandas_ta as ta
import json

def load_bars_from_db(db_path, symbol, timeframe):
    conn = sqlite3.connect(db_path)
    query = f"SELECT time, open, high, low, close, tick_volume FROM bars WHERE symbol = ? AND timeframe = ? ORDER BY time ASC"
    df = pd.read_sql(query, conn, params=(symbol, timeframe))
    conn.close()
    return df

def save_features_to_db(db_path, symbol, timeframe, df_features, feature_cols):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    features_data = []
    for _, row in df_features.iterrows():
        feature_json = json.dumps(row[feature_cols].to_dict())
        features_data.append((symbol, timeframe, row['time'], feature_json))
    cursor.executemany("INSERT OR IGNORE INTO features (symbol, timeframe, time, data) VALUES (?, ?, ?, ?)", features_data)
    conn.commit()
    conn.close()

def add_v1_features(df):
    # Standard calculation logic used by main loop
    df['ema_20'] = ta.ema(df['close'], length=20)
    df['rsi_14'] = ta.rsi(df['close'], length=14)
    return df.dropna()
