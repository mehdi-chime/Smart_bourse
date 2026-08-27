"""
Project : Smart_Bourse

File : history_downloader.py

Version : 2.0.0

Author :
Mehdi Jalali
ChatGPT

Description :
Professional History Downloader
"""

import json
import os
from datetime import datetime

from market.api import MarketAPI
from history.history_database import HistoryDatabase
from models.stock import Stock


class HistoryDownloader:

    def __init__(self):

        self.api = MarketAPI()

        self.db = HistoryDatabase()

        self.connected = False

        self.symbol = ""

        self.history = []

        self.last_update = None

        self.total_records = 0

        self.downloaded_days = 0

        self.save_path = "data/history"

        os.makedirs(self.save_path, exist_ok=True)
    # --------------------------------------------------

    def connect(self):

        print()

        print("=" * 60)
        print("Connecting To Market API")
        print("=" * 60)

        self.api.connect()

        self.connected = self.api.connected

        if self.connected:

            print("Market API Connected")

        else:

            print("Market API Connection Failed")

        return self.connected

    # --------------------------------------------------

    def disconnect(self):

        self.api.disconnect()

        self.connected = False

        print("Market API Disconnected")

    # --------------------------------------------------

    def is_connected(self):

        return self.connected

    # --------------------------------------------------

    def select_symbol(self, symbol):

        self.symbol = symbol.strip()

        print(f"Selected Symbol : {self.symbol}")

    # --------------------------------------------------

    def status(self):

        return {

            "connected": self.connected,

            "symbol": self.symbol,

            "records": len(self.history),

            "last_update": self.last_update

        }
    # --------------------------------------------------
    # --------------------------------------------------

    def download(self, days=365):

        if not self.connected:

            print("Not Connected To Market")

            return False

        if self.symbol == "":

            print("No Symbol Selected")

            return False

        print()

        print("=" * 60)
        print(f"Downloading History : {self.symbol}")
        print("=" * 60)
                # دریافت داده واقعی از API

        self.history = self.api.download_history(

            self.symbol,

            days

        )

        if not self.history:

            print("History Download Failed")

            return False

        

        self.downloaded_days = len(self.history)

        self.last_update = datetime.now()

        self.total_records = len(self.history)

        print(f"{self.total_records} Records Downloaded")

        return True
    # --------------------------------------------------

    def save_to_database(self):

        if not self.history:

            print("No History To Save")

            return False

        self.db.connect()

        self.db.create_tables()

        self.db.delete_symbol(self.symbol)

        stocks = []

        for item in self.history:

            stock = Stock()

            stock.symbol = self.symbol

            stock.trade_date = item["trade_date"]

            stock.open_price = item["open_price"]

            stock.high_price = item["high_price"]

            stock.low_price = item["low_price"]

            stock.close_price = item["close_price"]

            stock.volume = item["volume"]

            stocks.append(stock)

        self.db.insert_many(stocks)

        self.db.close()

        print(f"{len(stocks)} Records Saved To Database")

        return True
# --------------------------------------------------

    def save_json(self, filename=None):

        if not self.history:

            print("No History To Save")

            return False

        if filename is None:

            filename = os.path.join(

                self.save_path,

                f"{self.symbol.lower()}_history.json"

            )

        with open(filename, "w", encoding="utf-8") as file:

            json.dump(

                self.history,

                file,

                indent=4,

                ensure_ascii=False

            )

        print(f"History JSON Saved : {filename}")

        return True

    # --------------------------------------------------

    def load_json(self, filename):

        if not os.path.exists(filename):

            print("History File Not Found")

            return False

        with open(filename, "r", encoding="utf-8") as file:

            self.history = json.load(file)

        self.total_records = len(self.history)

        print(f"{self.total_records} Records Loaded")

        return True

    # --------------------------------------------------

    def show(self):

        print()

        print("=" * 70)

        print("HISTORY DOWNLOADER")

        print("=" * 70)

        print(f"Connected      : {self.connected}")

        print(f"Symbol         : {self.symbol}")

        print(f"Records        : {len(self.history)}")

        print(f"DownloadedDays : {self.downloaded_days}")

        if self.last_update:

            print(f"Last Update    : {self.last_update}")

        print("=" * 70)

    # --------------------------------------------------

    def update(self, days=365):

        print()

        print("Updating History...")

        if self.download(days):

            self.save_to_database()

            self.save_json()

            print("History Updated Successfully")

            return True

        return False
