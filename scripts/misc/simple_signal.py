import json

with open("data/market_today.json", "r", encoding="utf-8") as f:
    stocks = json.load(f)

print("📊 سیگنال‌های ساده بر اساس تغییرات روزانه:")
for s in stocks:
    change = (s['close_price'] - s['open_price']) / s['open_price'] * 100
    
    if change < -2:
        signal = "🟢 خرید"
    elif change > 2:
        signal = "🔴 فروش"
    else:
        signal = "⚪ هیچ"
    
    print(f"- {s['symbol']} | تغییرات: {change:+.2f}% | سیگنال: {signal}")
