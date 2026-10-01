"""
find_basing_stocks_advanced.py
پیدا کردن سهام با رشد کم + ورود پول حقیقی
"""

import json
import os
from datetime import datetime, timedelta
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

def get_real_money_flow(symbol):
    """دریافت ورود/خروج پول حقیقی از API"""
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
                # داده‌های کلاینت تایپ شامل خرید و فروش حقیقی/حقوقی است
                info = data.get("clientType", {})
                buy_real = info.get("buyReal", 0)
                sell_real = info.get("sellReal", 0)
                net_real = buy_real - sell_real
                return net_real
    except:
        return None
    return None

def find_basing_with_money(max_change=10, min_net_real=100_000_000):
    """
    پیدا کردن سهام با رشد کم و ورود پول حقیقی
    - max_change: حداکثر رشد قیمت (درصد)
    - min_net_real: حداقل ورود پول حقیقی (تومان)
    """
    symbols = get_all_symbols()
    results = []
    
    print(f"🔍 اسکن {len(symbols)} سهم...")
    
    for symbol in symbols:
        change = get_price_change(symbol, 180)
        if change is None or abs(change) > max_change:
            continue
        
        net_real = get_real_money_flow(symbol)
        if net_real is None or net_real < min_net_real:
            continue
        
        results.append({
            "symbol": symbol,
            "change": round(change, 2),
            "net_real": net_real
        })
    
    results.sort(key=lambda x: x['net_real'], reverse=True)
    return results

def report(results, top_n=20):
    if not results:
        print("❌ هیچ سهمی پیدا نشد.")
        return
    
    print("\n" + "=" * 70)
    print("📊 سهام با رشد کم + ورود پول حقیقی")
    print("=" * 70)
    print(f"تعداد: {len(results)}")
    print("=" * 70)
    
    for i, r in enumerate(results[:top_n], 1):
        print(f"{i}. {r['symbol']} | رشد: {r['change']:+.2f}% | ورود پول: {r['net_real']:,.0f}")

if __name__ == "__main__":
    results = find_basing_with_money(max_change=10, min_net_real=100_000_000)
    report(results)
