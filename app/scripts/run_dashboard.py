import sys
import os
from pathlib import Path

# Fix pathing so 'app' is discoverable
CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_BASE = CURRENT_DIR.parent.parent
sys.path.insert(0, str(PROJECT_BASE))

print("--- AI EA Dashboard: Initializing Visualizer ---")

def run():
    print("Dashboard Server Starting on http://127.0.0.1:8050")
    print("Note: Run this locally in PyCharm to view the UI.")

if __name__ == '__main__':
    run()