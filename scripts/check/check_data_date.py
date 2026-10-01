"""
check_data_date.py
بررسی آخرین تاریخ داده‌های لحظه‌ای و تاریخی
"""

import sys
import os
from pathlib import Path

# تنظیم مسیر
BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))

from database.database import Database
from history.history_database import HistoryDatabase
from market.api import MarketAPI


def check_live_data():
    """بررسی داده‌های لحظه‌ای خگستر"""
    print("\n📡 بررسی داده‌های لحظه‌ای...")
    
    db = Database()
    db.connect()
    inscode = db.get_inscode("خگستر")
    db.close()
    
    if not inscode:
        print("❌ InsCode خگستر پیدا نشد.")
        return
    
    api = MarketAPI()
    if api.connect():
        data = api.closing_price(inscode)
        if data:
            info = data.get("closingPriceInfo", {})
            print(f"✅ آخرین داده‌های لحظه‌ای خگستر:")
            print(f"   تاریخ: {info.get('tradeDate', 'نامشخص')}")
            print(f"   قیمت پایانی: {info.get('pClosing', 0):,.0f} ریال")
            print(f"   حجم: {info.get('qTotTran5J', 0):,.0f}")
        else:
            print("❌ داده‌ای دریافت نشد.")
        api.disconnect()


def check_history_data():
    """بررسی داده‌های تاریخی"""
    print("\n📆 بررسی داده‌های تاریخی...")
    
    history_db = HistoryDatabase()
    history_db.connect()
    
    # بررسی خگستر
    last_record = history_db.get_last_record("خگستر")
    if last_record:
        print(f"✅ آخرین تاریخ در دیتابیس برای خگستر: {last_record[1]}")
        print(f"   قیمت: {last_record[5]:,.0f} ریال")
    else:
        print("❌ هیچ داده‌ای برای خگستر در دیتابیس تاریخچه وجود ندارد.")
    
    # بررسی تعداد کل سهام با داده
    symbols = history_db.get_symbols()
    print(f"\n📊 تعداد کل سهام با داده‌ی تاریخی: {len(symbols)}")
    
    history_db.close()


def main():
    print("=" * 60)
    print("🔍 بررسی به‌روز بودن داده‌ها")
    print("=" * 60)
    
    check_live_data()
    check_history_data()
    
    print("\n" + "=" * 60)
    print("✅ بررسی کامل شد.")
    print("=" * 60)


if __name__ == "__main__":
    main()
