"""
bidar_scraper.py
جمع‌آوری داده‌های لحظه‌ای از Bidar Trader و ذخیره در قالب JSON
"""

import json
import os
from datetime import datetime

class BidarScraper:
    def __init__(self):
        self.data = {
            "symbol": "خگستر",
            "timestamp": datetime.now().isoformat(),
            "order_book": None,
            "price": None,
            "volume": None
        }
    
    def load_order_book(self, file_path="data/order_book_khegostar.json"):
        """بارگذاری صفوف خرید و فروش از فایل"""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                self.data["order_book"] = json.load(f)
            print("✅ Order Book بارگذاری شد.")
        except FileNotFoundError:
            print("❌ فایل order_book یافت نشد.")
    
    def load_price_data(self, file_path="data/market_today.json"):
        """بارگذاری داده‌های قیمت از فایل"""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                self.data["price"] = json.load(f)
            print("✅ داده‌های قیمت بارگذاری شدند.")
        except FileNotFoundError:
            print("❌ فایل قیمت یافت نشد.")
    
    def save_all(self, output_file="data/bidar_data.json"):
        """ذخیره همه داده‌ها در یک فایل"""
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)
        print(f"✅ همه داده‌ها در {output_file} ذخیره شدند.")
    
    def show_summary(self):
        """نمایش خلاصه داده‌ها"""
        print("\n📊 خلاصه داده‌های Bidar:")
        print(f"نماد: {self.data['symbol']}")
        print(f"زمان: {self.data['timestamp']}")
        if self.data.get("order_book"):
            print("✅ Order Book: موجود")
        if self.data.get("price"):
            print("✅ داده‌های قیمت: موجود")
        print("=" * 40)

if __name__ == "__main__":
    scraper = BidarScraper()
    scraper.load_order_book()
    scraper.load_price_data()
    scraper.show_summary()
    scraper.save_all()
