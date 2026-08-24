import sqlite3
import os
import random
from datetime import datetime

DB_PATH = os.path.join("database", "market.db")

def update_leaderboard(rank, bot_equity, leader_equity):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO leaderboard (rank, bot_equity, leader_equity) VALUES (?, ?, ?)", (rank, bot_equity, leader_equity))
        conn.commit()
        conn.close()
        print(f"[LEADERBOARD] Updated: Rank {rank}, Equity ${bot_equity:,.2f}")
    except Exception as e:
        print(f"[DB ERROR] {e}")

def simulate_competition(current_equity):
    """Simulates a live ranking update for testing logic."""
    mock_rank = random.randint(1, 50)
    # Leader equity is usually higher than the bot in simulation if rank is > 1
    mock_leader_equity = current_equity * (1.0 + random.uniform(0.01, 0.15)) if mock_rank > 1 else current_equity
    update_leaderboard(mock_rank, current_equity, mock_leader_equity)

if __name__ == '__main__':
    # Example simulation call
    simulate_competition(100000.0)