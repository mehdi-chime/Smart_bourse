"""
download_all_history.py
دانلود تاریخچه ۳۶۵ روزه برای همه سهام
"""

from database.database import Database
from history.history_downloader import HistoryDownloader

def main():
    print("📥 شروع دانلود تاریخچه همه سهام...")
    
    db = Database()
    db.connect()
    symbols = db.get_all_symbols()
    db.close()
    
    print(f"✅ {len(symbols)} نماد در دیتابیس پیدا شد.")
    
    downloader = HistoryDownloader()
    if not downloader.connect():
        print("❌ اتصال به بازار ممکن نیست.")
        return
    
    total = len(symbols)
    for idx, symbol_row in enumerate(symbols):
        symbol_name = symbol_row[1]
        
        if symbol_name.startswith('ح.'):
            continue
        
        if idx % 50 == 0:
            print(f"   دانلود {idx}/{total} ...")
        
        downloader.select_symbol(symbol_name)
        if downloader.download(365):
            downloader.save_to_database()
            downloader.save_json()
            print(f"   ✅ تاریخچه {symbol_name} دانلود شد.")
        else:
            print(f"   ❌ خطا در دانلود {symbol_name}")
    
    downloader.disconnect()
    print("✅ دانلود تاریخچه همه سهام کامل شد.")

if __name__ == "__main__":
    main()
