import json

# داده‌ای که از سایت گرفتی (برای تست)
raw_data = {
    "bestLimits": [
        {"number": 1, "qTitMeDem": 9000, "pMeDem": 3900.0, "pMeOf": 3920.0, "qTitMeOf": 38460771},
        {"number": 2, "qTitMeDem": 27907, "pMeDem": 3570.0, "pMeOf": 3930.0, "qTitMeOf": 169249},
        {"number": 3, "qTitMeDem": 8000, "pMeDem": 3480.0, "pMeOf": 3940.0, "qTitMeOf": 307527},
        {"number": 4, "qTitMeDem": 5020, "pMeDem": 3400.0, "pMeOf": 3950.0, "qTitMeOf": 575041},
        {"number": 5, "qTitMeDem": 4000, "pMeDem": 3370.0, "pMeOf": 3960.0, "qTitMeOf": 784527}
    ]
}

def analyze_order_book(data):
    """
    تحلیل صفوف خرید و فروش
    """
    buy_volume = sum(item["qTitMeDem"] for item in data["bestLimits"])
    sell_volume = sum(item["qTitMeOf"] for item in data["bestLimits"])
    avg_buy_price = sum(item["pMeDem"] * item["qTitMeDem"] for item in data["bestLimits"]) / buy_volume if buy_volume > 0 else 0
    avg_sell_price = sum(item["pMeOf"] * item["qTitMeOf"] for item in data["bestLimits"]) / sell_volume if sell_volume > 0 else 0
    
    pressure_ratio = buy_volume / sell_volume if sell_volume > 0 else 0
    
    return {
        "buy_volume": buy_volume,
        "sell_volume": sell_volume,
        "avg_buy_price": avg_buy_price,
        "avg_sell_price": avg_sell_price,
        "pressure_ratio": pressure_ratio,
        "signal": "🟢 فشار خرید" if pressure_ratio > 1.2 else "🔴 فشار فروش" if pressure_ratio < 0.8 else "⚪ متعادل"
    }

result = analyze_order_book(raw_data)

print("📊 تحلیل صفوف خرید و فروش:")
print(f"حجم خرید: {result['buy_volume']:,}")
print(f"حجم فروش: {result['sell_volume']:,}")
print(f"میانگین قیمت خرید: {result['avg_buy_price']:,.0f}")
print(f"میانگین قیمت فروش: {result['avg_sell_price']:,.0f}")
print(f"نسبت فشار: {result['pressure_ratio']:.2f}")
print(f"سیگنال: {result['signal']}")
