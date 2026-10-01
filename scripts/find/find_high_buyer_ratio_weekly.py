"""
find_high_buyer_ratio_weekly.py
پیدا کردن سهام با نسبت خریداران بالا در یک هفته اخیر (بر اساس حجم و قیمت)
"""

import pandas as pd
from datetime import datetime, timedelta
from history.history_database import HistoryDatabase
from database.database import Database

# ========== تنظیمات ==========
MIN_BUYER_RATIO = 3   # حداقل نسبت خریداران به فروشندگان در هفته
WEEK_DAYS = 7

def get_all_symbols():
    db = Database()
    db.connect()
    symbols = db.get_all_symbols()
    db.close()
    return [s[1] for s in symbols if len(s) > 1 and s[1]]

def get_weekly_data(symbol):
    """دریافت داده‌های یک هفته اخیر برای یک سهم"""
    history_db = HistoryDatabase()
    history_db.connect()
    stocks = history_db.get_history(symbol, WEEK_DAYS + 1)
    history_db.close()
    
    if len(stocks) < 2:
        return None
    
    # محاسبه تغییرات قیمت و حجم
    first_price = stocks[0].close_price
    last_price = stocks[-1].close_price
    avg_volume = sum(s.volume for s in stocks) / len(stocks)
    
    if first_price == 0:
        return None
    
    change = ((last_price - first_price) / first_price) * 100
    
    return {
        "change": change,
        "avg_volume": avg_volume,
        "last_price": last_price
    }

def find_high_buyer_ratio_weekly():
    symbols = get_all_symbols()
    results = []
    
    print(f"🔍 اسکن {len(symbols)} سهم برای یافتن نسبت خریداران بالا در یک هفته اخیر...")
    
    for symbol in symbols:
        data = get_weekly_data(symbol)
        if not data:
            continue
        
        # اگر حجم بالا و تغییرات مثبت باشد، یعنی خریداران قوی بوده‌اند
        if data['avg_volume'] > 50_000_000 and data['change'] > 0:
            results.append({
                "symbol": symbol,
                "change": round(data['change'], 2),
                "avg_volume": int(data['avg_volume']),
                "last_price": data['last_price']
            })
    
    # مرتب‌سازی بر اساس تغییرات (نزولی)
    results.sort(key=lambda x: x['change'], reverse=True)
    return results

def report(results, top_n=20):
    if not results:
        print("❌ هیچ سهمی در یک هفته اخیر با شرایط مورد نظر پیدا نشد.")
        return
    
    print("\n" + "=" * 90)
    print("📊 سهام با خریداران قوی در یک هفته اخیر")
    print("=" * 90)
    print(f"تعداد سهام پیدا شده: {len(results)}")
    print("=" * 90)
    
    for i, r in enumerate(results[:top_n], 1):
        print(f"{i:2}. {r['symbol']:8} | تغییرات: {r['change']:>+6.2f}% | میانگین حجم: {r['avg_volume']:>12,} | قیمت: {r['last_price']:>8,.0f}")

if __name__ == "__main__":
    print("📊 جستجوی سهام با خریداران قوی در یک هفته اخیر")
    print("=" * 90)
    
    results = find_high_buyer_ratio_weekly()
    report(results)
