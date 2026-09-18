import json

# داده‌ای که از سایت گرفتی
data = {
    "bestLimits": [
        {"number": 1, "qTitMeDem": 9000, "pMeDem": 3900.0, "pMeOf": 3920.0, "qTitMeOf": 38460771},
        {"number": 2, "qTitMeDem": 27907, "pMeDem": 3570.0, "pMeOf": 3930.0, "qTitMeOf": 169249},
        {"number": 3, "qTitMeDem": 8000, "pMeDem": 3480.0, "pMeOf": 3940.0, "qTitMeOf": 307527},
        {"number": 4, "qTitMeDem": 5020, "pMeDem": 3400.0, "pMeOf": 3950.0, "qTitMeOf": 575041},
        {"number": 5, "qTitMeDem": 4000, "pMeDem": 3370.0, "pMeOf": 3960.0, "qTitMeOf": 784527}
    ]
}

# ذخیره در فایل JSON
with open("data/order_book_khegostar.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("✅ فایل order_book_khegostar.json در پوشه data ذخیره شد.")
