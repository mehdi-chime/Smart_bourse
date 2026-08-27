"""
Project : Smart_Bourse

File : history_downloader.py

Version : 1.0.0

Author :
Mehdi Jalali
ChatGPT

Description :
Download Historical Market Data
"""
import json
import os
from datetime import datetime
from market.api import MarketAPI


class HistoryDownloader:

    def __init__(self):

        self.api = MarketAPI()

        self.connected = False

        self.symbol = ""

        self.history = []

        self.last_update = None

    # --------------------------------------------------

    def connect(self):

        self.api.connect()

        self.connected = self.api.connected

    # --------------------------------------------------

    def disconnect(self):

        self.connected = False

        print("Disconnected")

    # --------------------------------------------------

    def select_symbol(self, symbol):

        self.symbol = symbol

        print(f"Selected Symbol : {symbol}")

    # --------------------------------------------------

    def download(self, days=30):

        if not self.connected:

            print("Not Connected")

            return False

        self.history = self.api.download_history(

            self.symbol,

             days

         )
 
        self.last_update = datetime.now()

        print(f"{len(self.history)} Records Downloaded")

        return True      
                                                                                                                                      

    # --------------------------------------------------

    def save(self, filename=None):

        if not self.history:

            print("No History To Save")

            return

        if filename is None:

            filename = f"data/history/{self.symbol.lower()}_history.json"

        os.makedirs("data/history", exist_ok=True)

        with open(filename, "w", encoding="utf-8") as file:

            json.dump(self.history, file, indent=4, ensure_ascii=False)

        print(f"History Saved : {filename}")

    # --------------------------------------------------

    def load(self, filename):

        if not os.path.exists(filename):

            print("History File Not Found")

            return []

        with open(filename, "r", encoding="utf-8") as file:

            self.history = json.load(file)

        print(f"{len(self.history)} Records Loaded")

        return self.history

    # --------------------------------------------------

    def show(self):

        print()

        print("=" * 70)
        print("History Downloader")
        print("=" * 70)

        print(f"Connected : {self.connected}")
        print(f"Symbol    : {self.symbol}")
        print(f"Records   : {len(self.history)}")

        if self.last_update:

            print(f"Updated   : {self.last_update}")

        print("=" * 70)

    # --------------------------------------------------

    def status(self):

        return {

            "connected": self.connected,

            "symbol": self.symbol,

            "records": len(self.history),

            "last_update": self.last_update

        }

    # --------------------------------------------------

    def update(self):

        print("Updating History...")

        if self.symbol:

            self.download()

        else:

            print("No Symbol Selected")
