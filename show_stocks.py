import json

with open("data/market_today.json", "r", encoding="utf-8") as f:
    stocks = json.load(f)

print("📊 لیست سهام موجود در امروز:")
for s in stocks:
    print(f"- {s['symbol']} | قیمت پایانی: {s['close_price']} | حجم: {s['volume']:,}")
