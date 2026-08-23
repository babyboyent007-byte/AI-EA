import pandas as pd
from ..core.exceptions import MT5ConnectionError

class MT5Client:
    def __init__(self, server, login, password):
        self.server = server
        self.login = login
        self.password = password
        self.connected = False

    def connect(self):
        # Simulation for Colab Environment
        print(f"📡 Connecting to {self.server}...")
        self.connected = True
        return True

    def get_account_info(self):
        if not self.connected: raise MT5ConnectionError("Not connected.")
        return {"balance": 5000.0, "equity": 5000.0, "currency": "USD"}