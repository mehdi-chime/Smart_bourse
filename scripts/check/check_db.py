from database.database import Database

db = Database()
db.connect()

# دریافت لیست نمادها از جدول symbols
symbols = db.get_all_symbols()  # ← این متد باید وجود داشته باشد

print(f"✅ تعداد نمادها: {len(symbols)}")
for s in symbols[:5]:
    print(f"   - {s}")

db.close()
