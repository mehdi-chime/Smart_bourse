import os

folder = "history"
if os.path.exists(folder):
    files = os.listdir(folder)
    print(f"📂 فایل‌های موجود در پوشه '{folder}':")
    for f in files:
        print(f"   - {f}")
else:
    print(f"❌ پوشه '{folder}' وجود ندارد.")
