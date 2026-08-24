import pandas as pd
import numpy as np

class LeaderboardOptimizer:
    def __init__(self, target_rank=10, aggressive_gap=0.05):
        self.target_rank = target_rank
        self.aggressive_gap = aggressive_gap  # % gap behind leader to trigger Attack
        # Define Persona Parameters
        self.mode_params = {
            "ATTACK":  {"sizing_multiplier": 1.5, "stop_loss_scalar": 0.8, "description": "Aggressive recovery mode"},
            "DEFENSE": {"sizing_multiplier": 0.5, "stop_loss_scalar": 1.5, "description": "Lead preservation mode"},
            "GROWTH":  {"sizing_multiplier": 1.0, "stop_loss_scalar": 1.0, "description": "Standard balanced mode"}
        }

    def recommend_mode(self, current_rank, bot_equity, leader_equity):
        """
        Recommends a competition mode based on leaderboard position.
        """
        if current_rank <= self.target_rank:
            return "DEFENSE"
        
        equity_gap = (leader_equity - bot_equity) / leader_equity
        if equity_gap > self.aggressive_gap:
            return "ATTACK"
        
        return "GROWTH"

    def get_mode_params(self, mode):
        """
        Returns execution parameters for the specific persona.
        """
        return self.mode_params.get(mode, self.mode_params["GROWTH"])

if __name__ == "__main__":
    optimizer = LeaderboardOptimizer()
    # Example: Top 5 ranking test
    mode = optimizer.recommend_mode(5, 105000, 110000)
    params = optimizer.get_mode_params(mode)
    print(f"Recommended Mode: {mode} | Params: {params}")