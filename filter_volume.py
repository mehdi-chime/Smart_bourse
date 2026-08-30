import json

with open("data/market_today.json", "r", encoding="utf-8") as f:
    stocks = json.load(f)

print("🔍 فیلتر سهام با حجم بالای ۱ میلیارد:")
for s in stocks:
    if s['volume'] > 1_000_000_000:
        print(f"- {s['symbol']} | حجم: {s['volume']:,}")
