"""
find_basing_relative.py
پیدا کردن سهام با رشد کمتر از میانگین صنعت + ورود پول حقیقی
"""

import json
import os
from collections import defaultdict
from history.history_database import HistoryDatabase
from database.database import Database
from market.api import MarketAPI

def get_all_symbols():
    db = Database()
    db.connect()
    symbols = db.get_all_symbols()
    db.close()
    return [s[1] for s in symbols if len(s) > 1 and s[1]]

def get_price_change(symbol, days=180):
    history_db = HistoryDatabase()
    history_db.connect()
    stocks = history_db.get_history(symbol, days + 1)
    history_db.close()
    if len(stocks) < 2:
        return None
    first_price = stocks[0].close_price
    last_price = stocks[-1].close_price
    if first_price == 0:
        return None
    return ((last_price - first_price) / first_price) * 100

def get_sector(symbol):
    """دریافت صنعت سهم از دیتابیس"""
    db = Database()
    db.connect()
    cursor = db.connection.cursor()
    cursor.execute("SELECT sector_name FROM symbols WHERE symbol=?", (symbol,))
    row = cursor.fetchone()
    db.close()
    return row[0] if row else "نامشخص"

def get_real_money_flow(symbol):
    try:
        db = Database()
        db.connect()
        inscode = db.get_inscode(symbol)
        db.close()
        if not inscode:
            return None
        api = MarketAPI()
        if api.connect():
            data = api.client_type(inscode)
            api.disconnect()
            if data:
                info = data.get("clientType", {})
                buy_real = info.get("buyReal", 0)
                sell_real = info.get("sellReal", 0)
                return buy_real - sell_real
    except:
        return None
    return None

def find_basing_relative(min_net_real=50_000_000):
    """
    پیدا کردن سهام با رشد کمتر از میانگین صنعت
    """
    symbols = get_all_symbols()
    sector_data = defaultdict(list)
    
    # مرحله ۱: محاسبه رشد همه سهام و دسته‌بندی بر اساس صنعت
    print(f"🔍 مرحله ۱: محاسبه رشد {len(symbols)} سهم...")
    for symbol in symbols:
        change = get_price_change(symbol, 180)
        if change is not None:
            sector = get_sector(symbol)
            sector_data[sector].append({
                "symbol": symbol,
                "change": change
            })
    
    # مرحله ۲: محاسبه میانگین رشد هر صنعت
    sector_avg = {}
    for sector, stocks in sector_data.items():
        if len(stocks) > 1:
            avg = sum(s['change'] for s in stocks) / len(stocks)
            sector_avg[sector] = avg
    
    # مرحله ۳: پیدا کردن سهام با رشد کمتر از میانگین صنعت
    results = []
    for sector, stocks in sector_data.items():
        avg = sector_avg.get(sector, 0)
        for stock in stocks:
            if stock['change'] < avg * 0.8:  # حداقل ۲۰٪ کمتر از میانگین
                net_real = get_real_money_flow(stock['symbol'])
                if net_real is not None and net_real > min_net_real:
                    results.append({
                        "symbol": stock['symbol'],
                        "change": round(stock['change'], 2),
                        "sector_avg": round(avg, 2),
                        "diff": round(avg - stock['change'], 2),
                        "net_real": net_real
                    })
    
    results.sort(key=lambda x: x['diff'], reverse=True)
    return results

def report(results, top_n=20):
    if not results:
        print("❌ هیچ سهمی با رشد کمتر از میانگین صنعت پیدا نشد.")
        return
    
    print("\n" + "=" * 80)
    print("📊 سهام با رشد کمتر از میانگین صنعت + ورود پول حقیقی")
    print("=" * 80)
    print(f"تعداد: {len(results)}")
    print("=" * 80)
    
    for i, r in enumerate(results[:top_n], 1):
        print(f"{i}. {r['symbol']} | رشد: {r['change']:+.2f}% | میانگین صنعت: {r['sector_avg']:+.2f}% | اختلاف: {r['diff']:+.2f}% | ورود پول: {r['net_real']:,.0f}")

if __name__ == "__main__":
    results = find_basing_relative(min_net_real=50_000_000)
    report(results)
