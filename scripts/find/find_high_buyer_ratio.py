"""
find_high_buyer_ratio.py
پیدا کردن سهام با نسبت خریداران حقیقی به فروشندگان حقیقی بالا
"""

import os
import json
from market.api import MarketAPI
from database.database import Database

# ========== تنظیمات ==========
MIN_BUYER_RATIO = 10   # نسبت خریداران به فروشندگان حداقل ۱۰

def get_all_symbols():
    db = Database()
    db.connect()
    symbols = db.get_all_symbols()
    db.close()
    return [s[1] for s in symbols if len(s) > 1 and s[1]]

def get_client_type_data(symbol):
    """دریافت اطلاعات خریداران و فروشندگان حقیقی/حقوقی"""
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
                return {
                    "buy_real": info.get("buyReal", 0),      # تعداد خریداران حقیقی
                    "sell_real": info.get("sellReal", 0),    # تعداد فروشندگان حقیقی
                    "buy_legal": info.get("buyLegal", 0),    # تعداد خریداران حقوقی
                    "sell_legal": info.get("sellLegal", 0),  # تعداد فروشندگان حقوقی
                }
    except:
        return None
    return None

def find_high_buyer_ratio(min_ratio=MIN_BUYER_RATIO):
    symbols = get_all_symbols()
    results = []
    
    print(f"🔍 اسکن {len(symbols)} سهم برای یافتن نسبت خریداران حقیقی بالا...")
    
    for symbol in symbols:
        data = get_client_type_data(symbol)
        if not data:
            continue
        
        buy_real = data.get("buy_real", 0)
        sell_real = data.get("sell_real", 0)
        
        if sell_real == 0:
            continue
        
        ratio = buy_real / sell_real
        
        if ratio >= min_ratio:
            results.append({
                "symbol": symbol,
                "buy_real": buy_real,
                "sell_real": sell_real,
                "ratio": round(ratio, 2),
                "buy_legal": data.get("buy_legal", 0),
                "sell_legal": data.get("sell_legal", 0),
            })
    
    # مرتب‌سازی بر اساس نسبت (نزولی)
    results.sort(key=lambda x: x['ratio'], reverse=True)
    return results

def report(results, top_n=20):
    if not results:
        print("❌ هیچ سهمی با نسبت خریداران بالا پیدا نشد.")
        return
    
    print("\n" + "=" * 90)
    print("📊 سهام با نسبت خریداران حقیقی بالا")
    print("=" * 90)
    print(f"تعداد سهام پیدا شده: {len(results)}")
    print("=" * 90)
    
    for i, r in enumerate(results[:top_n], 1):
        print(f"{i:2}. {r['symbol']:8} | نسبت خرید/فروش: {r['ratio']:>6.2f} | خریداران: {r['buy_real']:>6} | فروشندگان: {r['sell_real']:>6} | حقوقی خرید: {r['buy_legal']:>6} | حقوقی فروش: {r['sell_legal']:>6}")

if __name__ == "__main__":
    print("📊 جستجوی سهام با نسبت خریداران حقیقی بالا")
    print(f"   حداقل نسبت: {MIN_BUYER_RATIO}")
    print("=" * 90)
    
    results = find_high_buyer_ratio()
    report(results)
