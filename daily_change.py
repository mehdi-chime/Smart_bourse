import json

with open("data/market_today.json", "r", encoding="utf-8") as f:
    stocks = json.load(f)

print("📈 تغییرات روزانه هر سهم:")
for s in stocks:
    change = (s['close_price'] - s['open_price']) / s['open_price'] * 100
    print(f"- {s['symbol']} | تغییرات: {change:+.2f}%")
