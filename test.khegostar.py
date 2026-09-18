from database.database import Database

db = Database()
db.connect()
symbols = db.get_all_symbols()
db.close()

found = False
for s in symbols:
    try:
        # بررسی اینکه s[1] یک string است
        if s[1] and "خگستر" in str(s[1]):
            print("✅ خگستر پیدا شد:")
            print(s)
            found = True
            break
    except:
        continue

if not found:
    print("❌ خگستر در دیتابیس پیدا نشد.")
