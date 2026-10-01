"""
Project : Smart_Bourse
File : market_downloader.py
Version : 5.0.0
Description : Download ALL market data from TSETMC
"""

from datetime import datetime
import os
import json
from market.api import MarketAPI
from database.database import Database

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

class MarketDownloader:
    def __init__(self):
        self.market_data = []
        self.data_folder = os.path.join(BASE_DIR, "data")
        os.makedirs(self.data_folder, exist_ok=True)
        self.json_file = os.path.join(self.data_folder, "market_today.json")
        self.api = MarketAPI()
        self.db = Database()

    def get_all_symbols(self):
        """دریافت لیست همه نمادها از دیتابیس"""
        try:
            self.db.connect()
            symbols = self.db.get_all_symbols()
            self.db.close()
            # استخراج نام فارسی نمادها
            return [s[1] for s in symbols if len(s) > 1 and s[1]]
        except Exception as e:
            print(f"❌ خطا در دریافت لیست نمادها: {e}")
            return []

    def download(self):
        print("[Downloader] Connecting To Market...")
        if not self.api.connect():
            print("[Downloader] Market Connection Failed")
            return False

        today = str(datetime.now().date())
        self.market_data = []

        # دریافت همه نمادها از دیتابیس
        symbols = self.get_all_symbols()
        if not symbols:
            # اگر دیتابیس خالی بود، از لیست پیش‌فرض استفاده کن
            symbols = ["فولاد", "فملی", "خودرو", "خگستر", "شپنا", "کگل", "وبملت", "فارس", "شستا", "حکشتی"]

        total = len(symbols)
        print(f"📊 {total} نماد برای دانلود پیدا شد.")

        for idx, symbol_fa in enumerate(symbols, 1):
            if idx % 50 == 0:
                print(f"   دانلود {idx}/{total} ...")

            try:
                # دریافت InsCode از دیتابیس
                self.db.connect()
                inscode = self.db.get_inscode(symbol_fa)
                self.db.close()

                if not inscode:
                    continue

                data = self.api.closing_price(inscode)
                if not data:
                    continue

                info = data.get("closingPriceInfo", data)
                if not info:
                    continue

                close_price = info.get("pClosing")
                if close_price is None:
                    continue

                record = {
                    "symbol": symbol_fa,
                    "trade_date": today,
                    "open_price": info.get("priceFirst"),
                    "high_price": info.get("priceMax"),
                    "low_price": info.get("priceMin"),
                    "close_price": close_price,
                    "volume": info.get("qTotTran5J") or 0
                }

                self.market_data.append(record)

            except Exception as e:
                print(f"Download Error [{symbol_fa}] : {e}")
                continue

        self.api.disconnect()
        print(f"\n✅ دانلود کامل شد: {len(self.market_data)} رکورد")
        return True

    def save_json(self):
        with open(self.json_file, "w", encoding="utf-8") as f:
            json.dump(self.market_data, f, ensure_ascii=False, indent=2)
        print(f"[Downloader] JSON Saved: {self.json_file}")

    def show(self):
        print("\n" + "=" * 45)
        print("Market Data")
        print("=" * 45)
        for stock in self.market_data[:10]:
            print(f"{stock['symbol']}: {stock['close_price']}")
        print(f"... و {len(self.market_data) - 10} سهم دیگر")
        print("=" * 45)
