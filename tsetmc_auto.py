import requests
import json
import os
from datetime import datetime

class TsetmcAuto:
    def __init__(self, ins_code="48990026850202503"):
        self.ins_code = ins_code
        self.base_url = "https://cdn.tsetmc.com/api"
        self.data = {}
        
    def fetch_price(self):
        """دریافت اطلاعات قیمت لحظه‌ای"""
        url = f"{self.base_url}/ClosingPrice/GetClosingPriceInfo/{self.ins_code}"
        response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
        if response.status_code == 200:
            self.data["price"] = response.json()
            return True
        return False
    
    def fetch_order_book(self):
        """دریافت صفوف خرید و فروش"""
        url = f"{self.base_url}/BestLimits/{self.ins_code}"
        response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
        if response.status_code == 200:
            self.data["order_book"] = response.json()
            return True
        return False
    
    def fetch_all(self):
        """دریافت همه داده‌ها"""
        print("📡 دریافت اطلاعات از TSETMC...")
        success = True
        if not self.fetch_price():
            print("❌ خطا در دریافت قیمت")
            success = False
        if not self.fetch_order_book():
            print("❌ خطا در دریافت صفوف")
            success = False
        return success
    
    def save(self):
        """ذخیره داده‌ها در فایل JSON"""
        os.makedirs("data", exist_ok=True)
        filename = f"data/tsetmc_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)
        print(f"✅ داده‌ها در {filename} ذخیره شد.")
        return filename
    
    def show_summary(self):
        """نمایش خلاصه"""
        price_info = self.data.get("price", {}).get("closingPriceInfo", {})
        order_info = self.data.get("order_book", {}).get("bestLimits", [])
        
        last_price = price_info.get("pClosing", 0)
        open_price = price_info.get("priceFirst", 0)
        volume = price_info.get("qTotTran5J", 0)
        
        buy_vol = sum(item.get("qTitMeDem", 0) for item in order_info)
        sell_vol = sum(item.get("qTitMeOf", 0) for item in order_info)
        
        print("\n" + "=" * 50)
        print("📊 خلاصه داده‌های خگستر")
        print("=" * 50)
        print(f"آخرین قیمت: {last_price:,.0f} ریال")
        print(f"قیمت بازگشایی: {open_price:,.0f} ریال")
        print(f"حجم معاملات: {volume:,.0f}")
        print(f"حجم خرید در صف: {buy_vol:,.0f}")
        print(f"حجم فروش در صف: {sell_vol:,.0f}")
        print("=" * 50)

if __name__ == "__main__":
    scraper = TsetmcAuto()
    if scraper.fetch_all():
        scraper.show_summary()
        scraper.save()
    else:
        print("❌ دریافت داده با مشکل مواجه شد.")
