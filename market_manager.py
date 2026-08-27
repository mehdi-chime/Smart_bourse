"""
Project : Smart_Bourse

File : market_manager.py

Version : 1.0.0

Author :
Mehdi Jalali
ChatGPT

Description :
Smart Market Manager
"""

from datetime import datetime

from database.database import Database


class MarketManager:

    def __init__(self):

        self.db = Database()

        self.stocks = []

        self.market_open = False

        self.symbols = [

            "Foolad",
            "Femeli",
            "Khodro",
            "Shasta",
            "Shepna"

        ]
    # --------------------------------------------------

    def is_market_open(self):

        now = datetime.now()

        weekday = now.weekday()

        hour = now.hour

        minute = now.minute

        if weekday in (3, 4):
            return False

        current = hour * 60 + minute

        start = 8 * 60 + 45

        end = 12 * 60 + 30

        return start <= current <= end

    # --------------------------------------------------

    def load(self, json_file):

        self.market_open = self.is_market_open()

        self.db.connect()

        self.stocks = self.db.get_all_stocks()

        self.db.close()

        return self.stocks
        # --------------------------------------------------

    def show(self):

        print()

        print("=" * 70)
        print("MARKET MANAGER")
        print("=" * 70)

        print(f"Market Open : {self.market_open}")
        print(f"Symbols     : {len(self.symbols)}")

        print("=" * 70)

    # --------------------------------------------------

    def run(self, json_file):

        self.load(json_file)

        print()

        print("=" * 70)
        print("SMART MARKET MANAGER")
        print("=" * 70)

        if self.market_open:

            print("Market Is Open")
            print("Online Data Mode")

        else:

            print("Market Is Closed")
            print("Database Mode")

        print()

        if not self.stocks:

            print("No Data In Database")
            return

        print("-" * 70)

        for stock in self.stocks:

            try:

                print(

                    f"{stock[0]:10} | "
                    f"{stock[1]} | "
                    f"Open:{stock[2]} | "
                    f"Close:{stock[5]} | "
                    f"Volume:{stock[6]}"

                )

            except Exception:

                pass

        print("-" * 70)
        # --------------------------------------------------

        def get_symbols(self):

            return self.symbols

        # --------------------------------------------------

        def get_stocks(self):

            return self.stocks

        # --------------------------------------------------

        def refresh(self, json_file):

            """
            Reload Market
            """

            self.load(json_file)

        # --------------------------------------------------

        def status(self):

            return {

                "market_open": self.market_open,

                "symbols": len(self.symbols),

                "stocks": len(self.stocks)

            }
