import os

def scan_folder(folder):
    if os.path.exists(folder):
        print(f"📂 محتویات پوشه: {folder}")
        for item in os.listdir(folder):
            print(f"   - {item}")
    else:
        print(f"❌ پوشه {folder} وجود ندارد.")

scan_folder("data")
scan_folder("data/history")
scan_folder("history")
