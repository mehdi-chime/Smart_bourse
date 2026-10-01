from history.history_database import HistoryDatabase
from database.database import Database

# دریافت لیست همه نمادها
db = Database()
db.connect()
symbols = db.get_all_symbols()
db.close()

# بررسی تعداد روزهای هر سهم
history_db = HistoryDatabase()
history_db.connect()

results = []
for s in symbols[:20]:  # فقط ۲۰ تای اول برای تست
    symbol_name = s[1]
    data = history_db.get_history(symbol_name, 9999)  # همه داده‌ها
    days = len(data)
    results.append((symbol_name, days))
    print(f"{symbol_name}: {days} روز")

history_db.close()
