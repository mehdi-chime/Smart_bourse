"""
Project : Smart_Bourse

File : updater.py

Version : 2.0.0

Author :
Mehdi Jalali
ChatGPT

Description :
Smart Database Updater
"""

from database.database import Database
from models.stock import Stock


class Updater:

    def __init__(self):

        self.db = Database()

        self.inserted = 0
        self.updated = 0
        self.skipped = 0

    # --------------------------------------------------

    def update(self, market_data):

        if len(market_data) == 0:

            print("No Data To Update")

            return False

        self.db.connect()

        self.db.create_tables()

        trade_date = market_data[0]["trade_date"]

        # حذف اطلاعات همان روز
        self.db.delete_by_date(trade_date)

        self.inserted = 0

        for item in market_data:

            stock = Stock()

            stock.symbol = item["symbol"]
            stock.trade_date = item["trade_date"]
            stock.open_price = item["open_price"]
            stock.high_price = item["high_price"]
            stock.low_price = item["low_price"]
            stock.close_price = item["close_price"]
            stock.volume = item["volume"]

            self.db.insert_stock(stock)

            self.inserted += 1


        self.db.close()

        return True

    # --------------------------------------------------

    def show(self):

        print()

        print("=" * 70)
        print("DATABASE UPDATE REPORT")
        print("=" * 70)

        print(f"Inserted : {self.inserted}")
        print(f"Updated  : {self.updated}")
        print(f"Skipped  : {self.skipped}")

        print("=" * 70)

    # --------------------------------------------------

    def status(self):

        return {

            "inserted": self.inserted,
            "updated": self.updated,
            "skipped": self.skipped

        }
