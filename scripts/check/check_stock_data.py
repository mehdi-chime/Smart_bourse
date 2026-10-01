"""
check_stock_data.py
بررسی داده‌های ذخیره‌شده برای چند سهم خاص
"""

from history.history_database import HistoryDatabase

def check_stock(symbol):
    """بررسی تعداد روزهای داده و آخرین قیمت یک سهم"""
    history_db = HistoryDatabase()
    history_db.connect()
    
    try:
        stocks = history_db.get_history(symbol, 9999)  # همه داده‌ها
        count = len(stocks)
        last_price = stocks[-1].close_price if count > 0 else 0
        last_date = stocks[-1].trade_date if count > 0 else "ندارد"
        
        print(f"\n📊 {symbol}:")
        print(f"   تعداد روزها: {count}")
        print(f"   آخرین قیمت: {last_price:,.0f} ریال")
        print(f"   آخرین تاریخ: {last_date}")
        return {"symbol": symbol, "count": count, "last_price": last_price, "last_date": last_date}
    except Exception as e:
        print(f"❌ خطا در بررسی {symbol}: {e}")
        return {"symbol": symbol, "error": str(e)}
    finally:
        history_db.close()

if __name__ == "__main__":
    symbols = ["کویر", "کچینی", "کگل", "کیمیا", "یلدا", "خگستر", "فولاد"]
    
    print("=" * 50)
    print("🔍 بررسی داده‌های سهام")
    print("=" * 50)
    
    for symbol in symbols:
        check_stock(symbol)
    
    print("\n" + "=" * 50)
    print("✅ بررسی کامل شد.")
    print("=" * 50)
