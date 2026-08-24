import joblib
import numpy as np
import os

class EnsembleEngine:
    def __init__(self, models_dir="models/"):
        self.models = {}
        model_files = {
            "lgbm": "lgbm_baseline.joblib",
            "xgb": "xgb_bench.joblib",
            "rf": "rf_bench.joblib"
        }
        for key, filename in model_files.items():
            path = os.path.join(models_dir, filename)
            if os.path.exists(path):
                self.models[key] = joblib.load(path)
                print(f"[ENSEMBLE] Loaded {filename}")
            else:
                print(f"[WARNING] Model file {path} not found.")

    def get_consensus_multiplier(self, X_input):
        if len(self.models) < 3:
            return 0.0
        votes = []
        confidences = []
        for name, model in self.models.items():
            prob = model.predict_proba(X_input)[0, 1]
            vote = 1 if prob >= 0.65 else 0
            votes.append(vote)
            confidences.append(prob)
        if sum(votes) >= 2:
            agreeing_conf = [c for i, c in enumerate(confidences) if votes[i] == 1]
            avg_conf = np.mean(agreeing_conf)
            multiplier = 1.0 + (avg_conf - 0.65) / 0.35
            return round(max(1.0, multiplier), 2)
        return 0.0

if __name__ == '__main__':
    print('Ensemble Voting Engine V1.0 initialized.')