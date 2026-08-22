import joblib
import numpy as np
import pandas as pd
import os

class ProbabilityEstimator:
    def __init__(self, model_path=None):
        self.model = None
        if model_path and os.path.exists(model_path):
            self.model = joblib.load(model_path)

    def estimate(self, features_df):
        if self.model is None:
            return 0.5, 0.0, 0.0

        probs = self.model.predict_proba(features_df)[-1]
        win_prob = probs[1]
        confidence = abs(win_prob - 0.5) * 2
        expected_return = 0.01 * confidence

        return win_prob, expected_return, confidence
