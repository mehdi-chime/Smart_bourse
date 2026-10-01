"""
full_scanner.py
اسکنر کامل بازار با استفاده از کلاس MarketScanner
"""

import json
import os
from datetime import datetime
from database.database import Database
from history.history_database import HistoryDatabase
from engines.market_scanner import MarketScanner

# ========== تنظیمات ==========
REPORT_FILE = "reports/full_scanner_report.txt"
LOG_FILE = "logs/full_scanner.log"

def log_message(msg):
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"[{datetime.now()}] {msg}\n")

def save_report(content):
    with open(REPORT_FILE, "w", encoding="utf-8") as f:
        f.write(content)

def get_all_symbols():
    """دریافت لیست تمام نمادها از دیتابیس"""
    try:
        db = Database()
        db.connect()
        symbols = db.get_all_symbols()
        db.close()
        log_message(f"{len(symbols)} نماد از دیتابیس دریافت شد")
        return symbols
    except Exception as e:
        log_message(f"خطا: {e}")
        return []

def get_stock_history(symbol_name):
    """دریافت تاریخچه قیمت یک سهم"""
    try:
        history_db = HistoryDatabase()
        history_db.connect()
        stocks = history_db.get_history(symbol_name, 365)
        history_db.close()
        return stocks
    except Exception as e:
        log_message(f"خطا در دریافت تاریخچه {symbol_name}: {e}")
        return None

def scan_all_stocks():
    """اسکن همه سهام با استفاده از کلاس MarketScanner"""
    log_message("شروع اسکن کامل")
    print("\n🔍 اسکن بازار در حال انجام است...")
    
    symbols = get_all_symbols()
    if not symbols:
        print("❌ هیچ نمادی پیدا نشد.")
        return []
    
    print(f"✅ {len(symbols)} نماد در دیتابیس پیدا شد.")
    
    scanner = MarketScanner()
    results = []
    total = len(symbols)
    
    for idx, symbol in enumerate(symbols):
        symbol_name = symbol[1]  # نام فارسی
        if symbol_name.startswith('ح.'):
            continue  # نادیده گرفتن نمادهای حقیقی
        
        if idx % 100 == 0:
            print(f"   تحلیل {idx}/{total} ...")
        
        # دریافت داده‌های تاریخچه
        stocks = get_stock_history(symbol_name)
        if not stocks or len(stocks) < 60:
            continue
        
        # تحلیل با کلاس MarketScanner
        result = scanner.scan_symbol(stocks)
        if result:
            results.append(result)
    
    log_message(f"تحلیل {len(results)} سهم با موفقیت انجام شد")
    return results

def generate_report(results):
    """تولید گزارش نهایی"""
    if not results:
        return "❌ هیچ داده‌ای برای تحلیل پیدا نشد."
    
    # جدا کردن بر اساس دسته‌بندی
    long_term = [r for r in results if r['category'] == 'LONG_TERM']
    swing = [r for r in results if r['category'] == 'SWING']
    weak = [r for r in results if r['category'] == 'WEAK']
    
    # مرتب‌سازی بر اساس امتیاز
    long_term.sort(key=lambda x: x['score'], reverse=True)
    swing.sort(key=lambda x: x['score'], reverse=True)
    
    lines = []
    lines.append("=" * 80)
    lines.append("📊 گزارش اسکنر کامل بازار")
    lines.append(f"📆 تاریخ: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    lines.append(f"📈 تعداد سهام بررسی‌شده: {len(results)}")
    lines.append(f"   🏦 بلندمدت: {len(long_term)}")
    lines.append(f"   🎯 نوسان‌گیری: {len(swing)}")
    lines.append(f"   ⚠️ ضعیف: {len(weak)}")
    lines.append("=" * 80)
    
    # ۱۰ سهم برتر برای بلندمدت
    lines.append("\n🏦 ۱۰ سهم برتر برای سرمایه‌گذاری بلندمدت:")
    lines.append("-" * 70)
    for i, r in enumerate(long_term[:10], 1):
        lines.append(f"{i}. {r['symbol']} | قیمت: {r['price']:,.0f} | امتیاز: {r['score']}")
        lines.append(f"   📝 دلیل: {', '.join(r['reasons'][:3])}")
        lines.append("")
    
    # ۱۰ سهم برتر برای نوسان‌گیری
    lines.append("\n🎯 ۱۰ سهم برتر برای نوسان‌گیری:")
    lines.append("-" * 70)
    for i, r in enumerate(swing[:10], 1):
        lines.append(f"{i}. {r['symbol']} | قیمت: {r['price']:,.0f} | امتیاز: {r['score']}")
        lines.append(f"   📝 دلیل: {', '.join(r['reasons'][:2])}")
        lines.append("")
    
    lines.append("=" * 80)
    return "\n".join(lines)

def main():
    print("\n" + "=" * 60)
    print("🔍 اسکنر کامل بازار Smart Bourse")
    print("📊 تحلیل همه سهام با کلاس MarketScanner")
    print("=" * 60)
    
    results = scan_all_stocks()
    
    if not results:
        print("❌ هیچ داده‌ای برای تحلیل پیدا نشد.")
        return
    
    report = generate_report(results)
    save_report(report)
    
    print("\n" + report)
    print(f"\n📁 گزارش در '{REPORT_FILE}' ذخیره شد.")
    log_message("اسکن کامل بازار تکمیل شد")

if __name__ == "__main__":
    main()
