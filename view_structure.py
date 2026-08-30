import json

with open("data/market_today.json", "r", encoding="utf-8") as f:
    data = json.load(f)

print("نوع داده:", type(data))
if isinstance(data, list):
    print("تعداد سهام:", len(data))
    print("نمونه اولین سهم:", data[0])
elif isinstance(data, dict):
    print("کلیدهای اصلی:", list(data.keys()))
