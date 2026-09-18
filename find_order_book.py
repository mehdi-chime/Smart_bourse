import os

folder = "data"
if os.path.exists(folder):
    files = os.listdir(folder)
    print("📂 فایل‌های موجود در پوشه 'data':")
    for f in files:
        print(f"   - '{f}'")  # با کوتیشن برای دیدن فضاهای اضافی
else:
    print("پوشه data وجود ندارد.")
