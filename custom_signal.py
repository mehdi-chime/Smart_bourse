import json

with open("data/market_today.json", "r", encoding="utf-8") as f:
    stocks = json.load(f)

print("📊 سیگنال بر اساس قانون شخصی شما (خرید زیر -۳٪ / فروش بالای +۳٪):")
for s in stocks:
    change = (s['close_price'] - s['open_price']) / s['open_price'] * 100
    
    if change < -3:
        signal = "🟢 پیشنهاد خرید"
    elif change > 3:
        signal = "🔴 پیشنهاد فروش"
    else:
        signal = "⏳ صبر کن (هنوز به حد نصاب نرسیده)"
    
    print(f"- {s['symbol']} | تغییرات: {change:+.2f}% | {signal}")
