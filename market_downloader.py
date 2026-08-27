"""
Project : Smart_Bourse

File : market_downloader.py

Version : 1.0.0

Description :
Download real market data from TSETMC and save JSON
"""

from datetime import datetime
import os

from utils.file_manager import FileManager
from market.api import MarketAPI
from database.symbol_repository import SymbolRepository


BASE_DIR = os.path.dirname(os.path.abspath(__file__))


class MarketDownloader:

    def __init__(self):

        self.market_data = []

        self.data_folder = os.path.join(
            BASE_DIR,
            "data"
        )

        os.makedirs(
            self.data_folder,
            exist_ok=True
        )

        self.json_file = os.path.join(
            self.data_folder,
            "market_today.json"
        )

        self.api = MarketAPI()
        self.repo = SymbolRepository()

        self.symbols = {
            "Foolad": "فولاد",
            "Femeli": "فملی",
            "Khodro": "خودرو"
        }

    # ----------------------------------

    def download(self):

        print("[Downloader] Connecting To Market...")

        if not self.api.connect():

            print("[Downloader] Market Connection Failed")

            return False

        today = str(datetime.now().date())

        self.market_data = []

        for symbol, symbol_fa in self.symbols.items():

            print()
            print("-" * 60)
            print("Downloading :", symbol)
            print("Persian Symbol :", symbol_fa)

            try:

                # Get InsCode from database
                inscode = self.repo.get_inscode(symbol_fa)

                print("DEBUG FOOLAD INSCODE =", inscode)

                if not inscode:

                    print("InsCode Not Found :", symbol_fa)
                    continue

                print("InsCode :", inscode)

                # Get real TSETMC price data
                data = self.api.closing_price(inscode)

                if not data:

                    print("No Closing Price Data")
                    continue

                # TSETMC response wrapper
                info = data.get(
                    "closingPriceInfo",
                    data
                )

                if not info:

                    print("Closing Price Info Not Found")
                    continue

                # ----------------------------------
                # Real market values
                # ----------------------------------

                open_price = info.get("priceFirst")
                high_price = info.get("priceMax")
                low_price = info.get("priceMin")
                close_price = info.get("pClosing")
                volume = info.get("qTotTran5J")

                if close_price is None:

                    print("Close Price Not Found")
                    continue

                record = {

                    "symbol": symbol,

                    "trade_date": today,

                    "open_price": open_price,

                    "high_price": high_price,

                    "low_price": low_price,

                    "close_price": close_price,

                    "volume": volume or 0

                }

                self.market_data.append(record)

                print("REAL MARKET DATA:")
                print(record)

            except Exception as e:

                print(
                    f"Download Error [{symbol}] : {e}"
                )

                continue

        self.api.disconnect()

        print()
        print("=" * 60)
        print("SYMBOL DOWNLOAD FINISHED")
        print("=" * 60)

        print(
            "Downloaded :",
            len(self.market_data)
        )

        print("=" * 60)

        return True

    # ----------------------------------

    def save_json(self):

        FileManager.save_json(
            self.json_file,
            self.market_data
        )

        print("[Downloader] JSON Saved")
        print(self.json_file)

    # ----------------------------------

    def load_json(self):

        self.market_data = FileManager.load_json(
            self.json_file
        )

        print("[Downloader] JSON Loaded")

    # ----------------------------------

    def show(self):

        print()

        print("=" * 45)
        print("Market Data")
        print("=" * 45)

        for stock in self.market_data:

            print(stock)

        print("=" * 45)
