"""
show_db.py
نمایش محتویات دیتابیس market_data.db با استفاده از پایتون
"""

import sqlite3
import os

DB_PATH = "data/market_data.db"

def show_tables():
    """نمایش همه جدول‌های دیتابیس"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    conn.close()
    return [t[0] for t in tables]

def show_table_content(table_name, limit=10):
    """نمایش محتویات یک جدول"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # دریافت ستون‌ها
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = [col[1] for col in cursor.fetchall()]
    
    # دریافت داده‌ها
    cursor.execute(f"SELECT * FROM {table_name} ORDER BY id DESC LIMIT {limit}")
    rows = cursor.fetchall()
    conn.close()
    
    return columns, rows

def main():
    if not os.path.exists(DB_PATH):
        print(f"❌ فایل {DB_PATH} وجود ندارد.")
        print("💡 لطفاً ابتدا DataFetcher را اجرا کنید:")
        print("   python core/data_fetcher.py")
        return
    
    print("\n📂 دیتابیس: " + DB_PATH)
    print("=" * 60)
    
    tables = show_tables()
    if not tables:
        print("❌ هیچ جدولی در دیتابیس پیدا نشد.")
        return
    
    print("📋 جدول‌های موجود:")
    for t in tables:
        print(f"   - {t}")
    
    print("\n" + "=" * 60)
    
    for table in tables:
        print(f"\n📊 محتویات جدول '{table}' (۱۰ رکورد آخر):")
        print("-" * 60)
        
        columns, rows = show_table_content(table)
        
        if not rows:
            print("   (جدول خالی است)")
            continue
        
        # نمایش ستون‌ها
        print("   " + " | ".join(columns))
        print("   " + "-" * 50)
        
        for row in rows:
            print("   " + " | ".join(str(r) for r in row))

if __name__ == "__main__":
    main()
