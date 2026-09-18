"""
find_basing_stocks.py
پیدا کردن سهام با رشد کم در ۶ ماه گذشته (کف‌سازی)
"""

import json
import os
from datetime import datetime, timedelta
from history.history_database import HistoryDatabase
from database.database import Database

def get_all_symbols():
    """دریافت لیست همه نمادها از دیتابیس"""
    db = Database()
    db.connect()
    symbols = db.get_all_symbols()
    db.close()
    return [s[1] for s in symbols if len(s) > 1 and s[1]]

def get_price_change(symbol, days=180):
    """محاسبه درصد تغییر قیمت در یک بازه زمانی"""
    history_db = HistoryDatabase()
    history_db.connect()
    
    # دریافت داده‌های تاریخی
    stocks = history_db.get_history(symbol, days + 1)
    history_db.close()
    
    if len(stocks) < 2:
        return None
    
    # قیمت اولیه و نهایی
    first_price = stocks[0].close_price
    last_price = stocks[-1].close_price
    
    if first_price == 0:
        return None
    
    change_percent = ((last_price - first_price) / first_price) * 100
    return change_percent

def find_basing_stocks(min_days=180, max_change=10):
    """
    پیدا کردن سهام با رشد کم (کف‌سازی)
    - min_days: حداقل روزهای تاریخی
    - max_change: حداکثر تغییرات (درصد)
    """
    symbols = get_all_symbols()
    results = []
    
    print(f"🔍 اسکن {len(symbols)} سهم برای یافتن سهام با رشد کمتر از {max_change}% در ۶ ماه...")
    
    for symbol in symbols:
        change = get_price_change(symbol, min_days)
        if change is not None and abs(change) < max_change:
            results.append({
                "symbol": symbol,
                "change": round(change, 2)
            })
    
    # مرتب‌سازی بر اساس تغییرات
    results.sort(key=lambda x: x['change'])
    
    return results

def report(results, top_n=20):
    """نمایش گزارش"""
    if not results:
        print("❌ هیچ سهمی با رشد کم پیدا نشد.")
        return
    
    print("\n" + "=" * 60)
    print("📊 سهام با رشد کم در ۶ ماه گذشته (کف‌سازی)")
    print("=" * 60)
    print(f"تعداد سهام پیدا شده: {len(results)}")
    print("=" * 60)
    
    for i, r in enumerate(results[:top_n], 1):
        print(f"{i}. {r['symbol']}: {r['change']:+.2f}%")

if __name__ == "__main__":
    results = find_basing_stocks(min_days=180, max_change=10)
    report(results)
