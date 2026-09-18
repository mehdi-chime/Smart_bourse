"""
core/data_fetcher.py
دریافت خودکار داده‌های لحظه‌ای از TSETMC
نسخه ۳.۰ - سرعت ۲ ثانیه - خاموشی هوشمند در زمان بسته بودن بازار
"""

import requests
import sqlite3
from datetime import datetime
import time
import os

# ========== تنظیمات ==========
MARKET_OPEN = "08:45"
MARKET_CLOSE = "12:30"
FETCH_INTERVAL = 2  # هر ۲ ثانیه (برای معاملات لحظه‌ای)
SILENT_MODE = True  # بعد از بسته شدن بازار، فقط یک بار پیام بده

class DataFetcher:
    def __init__(self, db_path="data/market_data.db"):
        self.db_path = db_path
        self.base_url = "https://cdn.tsetmc.com/api"
        os.makedirs("data", exist_ok=True)
        self.setup_database()
        self.market_closed_message_sent = False  # برای جلوگیری از تکرار پیام
    
    def setup_database(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS live_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT,
                ins_code TEXT,
                price REAL,
                volume REAL,
                buy_volume REAL,
                sell_volume REAL,
                timestamp TEXT
            )
        """)
        conn.commit()
        conn.close()
        print("✅ دیتابیس داده‌های لحظه‌ای آماده شد.")
    
    def is_market_open(self):
        now = datetime.now().time()
        start = datetime.strptime(MARKET_OPEN, "%H:%M").time()
        end = datetime.strptime(MARKET_CLOSE, "%H:%M").time()
        return start <= now <= end
    
    def fetch_price(self, ins_code):
        url = f"{self.base_url}/ClosingPrice/GetClosingPriceInfo/{ins_code}"
        try:
            response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=5)
            if response.status_code == 200:
                return response.json()
        except:
            pass
        return None
    
    def fetch_order_book(self, ins_code):
        url = f"{self.base_url}/BestLimits/{ins_code}"
        try:
            response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=5)
            if response.status_code == 200:
                return response.json()
        except:
            pass
        return None
    
    def save_live_data(self, symbol, ins_code):
        price_data = self.fetch_price(ins_code)
        order_data = self.fetch_order_book(ins_code)
        
        if not price_data and not order_data:
            return False
        
        price_info = price_data.get("closingPriceInfo", {}) if price_data else {}
        order_info = order_data.get("bestLimits", []) if order_data else []
        
        buy_volume = sum(item.get("qTitMeDem", 0) for item in order_info)
        sell_volume = sum(item.get("qTitMeOf", 0) for item in order_info)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO live_data (symbol, ins_code, price, volume, buy_volume, sell_volume, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            symbol,
            ins_code,
            price_info.get("pClosing", 0),
            price_info.get("qTotTran5J", 0),
            buy_volume,
            sell_volume,
            datetime.now().isoformat()
        ))
        conn.commit()
        conn.close()
        
        print(f"✅ {symbol} | قیمت: {price_info.get('pClosing', 0):,.0f} | خرید: {buy_volume:,} | فروش: {sell_volume:,} | {datetime.now().strftime('%H:%M:%S')}")
        return True
    
    def run_forever(self, symbol="خگستر", ins_code="48990026850202503", interval=FETCH_INTERVAL):
        print(f"🚀 شروع دریافت داده‌های لحظه‌ای برای {symbol}...")
        print(f"⏱️  فاصله هر {interval} ثانیه")
        print(f"⏰ ساعات معاملاتی: {MARKET_OPEN} تا {MARKET_CLOSE}")
        print("=" * 60)
        
        while True:
            if self.is_market_open():
                self.market_closed_message_sent = False  # ریست پیام بسته بودن
                try:
                    self.save_live_data(symbol, ins_code)
                except Exception as e:
                    print(f"❌ خطا: {e}")
            else:
                if not self.market_closed_message_sent:
                    print(f"⏳ بازار بسته است. منتظر شروع معاملات در {MARKET_OPEN} ...")
                    self.market_closed_message_sent = True
            
            time.sleep(interval)

if __name__ == "__main__":
    fetcher = DataFetcher()
    fetcher.run_forever()
