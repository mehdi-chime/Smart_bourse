"""
tsetmc_all_symbols.py
دریافت داده‌های لحظه‌ای برای همه نمادهای موجود در دیتابیس
"""

import requests
import json
import os
from datetime import datetime
from database.database import Database

class TsetmcAllSymbols:
    def __init__(self):
        self.base_url = "https://cdn.tsetmc.com/api"
        self.data = {}
        self.results = []
        
    def get_all_symbols(self):
        """دریافت لیست همه نمادها از دیتابیس"""
        db = Database()
        db.connect()
        symbols = db.get_all_symbols()
        db.close()
        return symbols
    
    def fetch_price(self, ins_code):
        """دریافت اطلاعات قیمت یک نماد"""
        url = f"{self.base_url}/ClosingPrice/GetClosingPriceInfo/{ins_code}"
        try:
            response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, proxies={}, timeout=10)
            if response.status_code == 200:
                return response.json()
        except:
            pass
        return None
    
    def fetch_order_book(self, ins_code):
        """دریافت صفوف خرید و فروش یک نماد"""
        url = f"{self.base_url}/BestLimits/{ins_code}"
        try:
            response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, proxies={}, timeout=10)
            if response.status_code == 200:
                return response.json()
        except:
            pass
        return None
    
    def fetch_all(self):
        """دریافت داده‌های همه نمادها"""
        symbols = self.get_all_symbols()
        print(f"📡 دریافت اطلاعات برای {len(symbols)} نماد...")
        
        for idx, symbol_row in enumerate(symbols):
            symbol_name = symbol_row[1]  # نام فارسی
            ins_code = symbol_row[5]     # InsCode
            
            if not ins_code:
                continue
            
            if idx % 50 == 0:
                print(f"   پردازش {idx}/{len(symbols)} ...")
            
            price_data = self.fetch_price(ins_code)
            order_data = self.fetch_order_book(ins_code)
            
            if price_data or order_data:
                self.results.append({
                    "symbol": symbol_name,
                    "ins_code": ins_code,
                    "price": price_data,
                    "order_book": order_data,
                    "timestamp": datetime.now().isoformat()
                })
        
        print(f"✅ داده‌های {len(self.results)} نماد دریافت شد.")
        return self.results
    
    def save(self):
        """ذخیره همه داده‌ها در یک فایل JSON"""
        os.makedirs("data", exist_ok=True)
        filename = f"data/tsetmc_all_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(self.results, f, ensure_ascii=False, indent=2)
        print(f"✅ همه داده‌ها در {filename} ذخیره شد.")
        return filename

if __name__ == "__main__":
    scraper = TsetmcAllSymbols()
    scraper.fetch_all()
    scraper.save()
