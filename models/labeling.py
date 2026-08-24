import sqlite3
import pandas as pd
import numpy as np

def add_multi_objective_labels(df, horizon=20):
    df['target_return'] = df['close'].shift(-horizon) / df['close'] - 1
    # Simplified success logic for main retrain loop
    df['target_success'] = (df['close'].shift(-3) > df['close']).astype(int)
    return df.dropna()
