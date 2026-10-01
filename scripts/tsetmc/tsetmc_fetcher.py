import requests
import json
import os

# ========== آدرس API واقعی ==========
URL = "https://cdn.tsetmc.com/api/ClosingPrice/GetClosingPriceInfo/48990026850202503"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

# ========== پوشه خروجی ==========
os.makedirs("data", exist_ok=True)

# ========== دریافت داده ==========
try:
    response = requests.get(URL, headers=HEADERS)
    
    if response.status_code == 200:
        data = response.json()
        
        with open("data/tsetmc_price.json", "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print("✅ داده‌های قیمت با موفقیت دریافت و در data/tsetmc_price.json ذخیره شد.")
    else:
        print(f"❌ خطا: {response.status_code}")

except Exception as e:
    print(f"❌ خطا در اتصال: {e}")
